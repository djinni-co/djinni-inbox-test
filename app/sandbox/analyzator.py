import base64
import datetime
import time
import faiss
from sentence_transformers import SentenceTransformer, util
from .models import MessageThread, JobPosting

class Analyzator:
    def __init__(self):
        self.hg_sentence_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        self.faiss_index = None

    def calc_priority(self, thread: MessageThread):
        res_score = 0
        job, candidate = thread.job, thread.candidate

        # Manual criterions
        # remote criterion
        remote_criterion = job.remote_type == JobPosting.RemoteType.OFFICE and job.location == candidate.location or candidate.can_relocate
        if remote_criterion:
            res_score += 5

        # uninterested_company_type_criterion
        if job.company_type is not None and candidate.uninterested_company_types is not None:
            uninterested_company_type_criterion = job.company_type in candidate.uninterested_company_types
            if uninterested_company_type_criterion:
                res_score -= 5

        # english_level_criterion
        english_level_criterion = job.english_level == candidate.english_level
        if english_level_criterion:
            res_score += 5
        ####

        # intersection of properties with same name
        prop_names_intersection = set(job.__dict__.keys()).intersection(candidate.__dict__.keys())
        prop_names_intersection.remove("_state")

        job_inter_attrs = self.get_inter_attr(prop_names_intersection, job)
        candidate_inter_attrs = self.get_inter_attr(prop_names_intersection, candidate)
        res_score += self.IOU(job_inter_attrs, candidate_inter_attrs)

        return res_score

    def get_candidate_job_distance(self, thread: MessageThread):
        messages = thread.message_set.all().order_by('created')
        # add all messages
        acc_candidate_data = " ".join(msg.body for msg in messages if msg.body is not None)

        # add extra info
        if thread.candidate.skills_cache is not None and thread.candidate.moreinfo is not None:
            acc_candidate_data += thread.candidate.skills_cache + " " + thread.candidate.moreinfo

        acc_candidate_data = acc_candidate_data.replace('\n', '')  # preprocess

        emb1 = self.hg_sentence_model.encode(acc_candidate_data, convert_to_tensor=True)
        emb2 = self.hg_sentence_model.encode(thread.job.long_description, convert_to_tensor=True)

        distance = util.pytorch_cos_sim(emb1, emb2)
        return round(distance.numpy()[0][0], 3)

    # utils
    def get_inter_attr(self, names_inter, item):
        res = []
        for x in names_inter:
            attr = getattr(item, x)
            if x is isinstance(attr, datetime.date):
                x = x.strftime('%m/%d/%Y')

            res.append(attr)

        return res

    def IOU(self, list1, list2):
        list1 = set(list1)
        list2 = set(list2)

        intersection = len(list1.intersection(list2))
        union = len(list1.union(list2))
        return intersection / union

    #FAISS
    def read_faiss_index(self, faiss_index_path):
        self.faiss_index = faiss.read_index(faiss_index_path)

    def faiss_search(self, text, k=10):
        text = text.replace('\n', ' ')  # preprocess

        embeddings = self.hg_sentence_model.encode(text, convert_to_tensor=True)
        D, I = self.faiss_index.search(embeddings.reshape(1, embeddings.shape[0]), k)

        return D, I


    def create_faiss_index(self, threads: [MessageThread], index_name):
        ids = []
        candidates_text_data = []
        for index, thread in enumerate(threads):
            messages = thread.message_set.all().order_by('created')  # this is can be changeable  with time !!!
            text = " ".join(msg.body for msg in messages if msg.body is not None)

            if thread.candidate.skills_cache is not None and thread.candidate.moreinfo is not None:
                text = thread.candidate.skills_cache + " " + thread.candidate.moreinfo

                text = text.replace('\n', ' ')  # preprocess
                candidates_text_data.append(text)

                ids.append(index) # id should be here (ids should be int) and it's incorrect to use index but I cannot unhash int value

        batch_size = 10
        emb_shape = 384
        index = faiss.IndexFlatL2(emb_shape)
        index2 = faiss.IndexIDMap(index)  # conversion needed to store with ids

        start_time = time.time()
        for i in range(0, len(candidates_text_data), batch_size):
            embeddings = self.hg_sentence_model.encode(candidates_text_data[i:i+batch_size], convert_to_tensor=True)
            index2.add_with_ids(embeddings, ids[i:i+batch_size])
            print(f"batch {i} from {len(candidates_text_data)}")

        end_time = time.time() - start_time
        print("Time to create embs ", end_time-start_time)

        faiss.write_index(index2, f'{index_name}')

