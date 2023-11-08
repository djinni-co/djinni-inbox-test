import time
import faiss
from sentence_transformers import SentenceTransformer, util

from django.db import models
from .models import MessageThread

class Analyzator:
    def __init__(self):
        self.hg_sentence_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        self.faiss_index = None

    def get_candidate_job_similarity(self, thread: MessageThread):
        messages = thread.message_set.all().order_by('created')

        acc_candidate_str = self.convert_model_to_string(thread.candidate)

        # Should I add messages here?
        acc_candidate_str += " ".join(msg.body for msg in messages if msg.body is not None)

        job_str = self.convert_model_to_string(thread.job)

        emb1 = self.hg_sentence_model.encode(acc_candidate_str, convert_to_tensor=True)
        emb2 = self.hg_sentence_model.encode(job_str, convert_to_tensor=True)

        similarity = util.pytorch_cos_sim(emb1, emb2)
        return round(similarity.numpy()[0][0], 3)

    # utils

    def convert_model_to_string(self, model: models.Model):
        model_str = str(model.__dict__)

        # primitive preprocess
        model_str.replace("\n", " ")
        model_str.replace("?", " ")
        model_str.replace("\r", " ")
        #
        return model_str


    #FAISS
    def read_faiss_index(self, faiss_index_path):
        self.faiss_index = faiss.read_index(faiss_index_path)

    def faiss_search(self,  job: models.Model, k=10):
        job_str = self.convert_model_to_string(job)

        embeddings = self.hg_sentence_model.encode(job_str, convert_to_tensor=True)
        D, I = self.faiss_index.search(embeddings.reshape(1, embeddings.shape[0]), k)

        return D, I

    def create_faiss_index(self, threads: [MessageThread], index_name):
        ids = []
        candidates_text_data = []

        for index, thread in enumerate(threads):
            messages = thread.message_set.all().order_by('created')
            acc_candidate_str = self.convert_model_to_string(thread.candidate)

            # Should I add messages here? (message is changeable data)
            acc_candidate_str += " ".join(msg.body for msg in messages if msg.body is not None)

            candidates_text_data.append(acc_candidate_str)

            ids.append(index) # id should be here (ids should be int) and it's incorrect to use index but I cannot unhash int value


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

