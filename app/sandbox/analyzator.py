import time
import json
import datetime
import faiss

from sentence_transformers import SentenceTransformer, util
from sklearn import decomposition

from django.db import models
from .models import MessageThread, JobPosting

class Analyzator:
    def __init__(self):
        self.hg_sentence_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        self.faiss_index = None
        self.init_distances = None

    def PCA(self, cand_embeddings, job_embedding):
        pca = decomposition.PCA(n_components=3)

        cand_pca = pca.fit_transform(cand_embeddings.numpy())
        job_pca = pca.transform(job_embedding.numpy()[None])

        return cand_pca, job_pca

    def dist(self, emb1, emb2):
        return util.pytorch_cos_sim(emb1, emb2)

    def get_candidate_job_similarity(self, thread: MessageThread, selected_job: JobPosting):
        messages = thread.message_set.all().order_by('created')

        acc_candidate_str = self.model_to_string(thread.candidate)

        # Should I add messages here?
        acc_candidate_str += " ".join(msg.body for msg in messages if msg.body is not None)

        job_str = self.model_to_string(selected_job) #thread.job)

        emb1 = self.hg_sentence_model.encode(acc_candidate_str, convert_to_tensor=True)
        emb2 = self.hg_sentence_model.encode(job_str, convert_to_tensor=True)

        similarity = self.dist(emb1, emb2)
        return round(similarity.numpy()[0][0], 3)

    # utils
    def model_to_string(self, model: models.Model):
        model_str = str(Analyzator.model_to_dict(model))

        # primitive preprocess
        model_str.replace("\n", " ")
        model_str.replace("?", " ")
        model_str.replace("\r", " ")
        #
        return model_str

    @staticmethod
    def model_to_dict(model: models.Model):
        model_dict = model.__dict__.copy()

        if "_state" in model_dict:
            model_dict.pop('_state', None)

        for key, value in model_dict.items():
            if isinstance(value, datetime.date):
                model_dict[key] = value.strftime('%m/%d/%Y')

        return model_dict

    #FAISS
    def read_faiss_index(self, faiss_index_path):
        self.faiss_index = faiss.read_index(faiss_index_path)

    def faiss_search(self,  job: models.Model, k=10):
        job_str = self.model_to_string(job)

        embeddings = self.hg_sentence_model.encode(job_str, convert_to_tensor=True)
        D, I = self.faiss_index.search(embeddings.reshape(1, embeddings.shape[0]), k)

        return D, I

    def create_faiss_index(self, threads: [MessageThread], index_name):
        ids = []
        candidates_text_data = []

        for index, thread in enumerate(threads):
            messages = thread.message_set.all().order_by('created')
            acc_candidate_str = self.model_to_string(thread.candidate)

            # Should I add messages here? (message is changeable data)
            acc_candidate_str += " ".join(msg.body for msg in messages if msg.body is not None)

            candidates_text_data.append(acc_candidate_str)

            ids.append(thread.candidate_id)


        # Inference
        batch_size = 10
        emb_shape = 384
        index = faiss.IndexFlatL2(emb_shape)
        index2 = faiss.IndexIDMap(index)  # conversion needed to store with ids

        start_time = time.time()
        for i in range(0, len(candidates_text_data), batch_size):
            embeddings = self.hg_sentence_model.encode(candidates_text_data[i:i+batch_size], convert_to_tensor=True)
            index2.add_with_ids(embeddings, ids[i:i+batch_size])
            print(f"batch {i} from {len(candidates_text_data)}")

        exec_time = time.time() - start_time
        print("Time to create embs ", exec_time)

        faiss.write_index(index2, f'{index_name}')

    # Simplify experimental design
    @staticmethod
    def convert_db_to_json(path='data.json'):
        mg_db_json = {}

        all_jobs = JobPosting.objects.all()
        for index, job in enumerate(all_jobs):
            job_dict = Analyzator.model_to_dict(job)

            job_threads = MessageThread.objects.filter(job=job)

            if len(job_threads) == 0: continue  # can be used for test but skipped for now

            for th_index, thread in enumerate(job_threads):
                thread_dict = Analyzator.model_to_dict(thread)
                candidate_dict = Analyzator.model_to_dict(thread.candidate)

                if "candidates" not in job_dict:
                    job_dict["candidates"] = []

                job_dict["candidates"].append({"candidate": candidate_dict, "thread": thread_dict})

            d_key = f"job_{index}"
            mg_db_json[d_key] = job_dict

        with open(path, 'w') as f:
            json.dump(mg_db_json, f)
            print("db dumped to", path)

