import os

import time

import numpy as np
from django.shortcuts import render

from .analyzator import Analyzator

from .models import Recruiter, MessageThread, JobPosting

# Hardcode for logged in as recruiter
RECRUITER_ID = 125528

faiss_index_path = "faissIDMap2.index"
analyzator = Analyzator()
analyzator.read_faiss_index(faiss_index_path)

TEST_THREAD_INDEX = 0  # needed to select job posting for test
TEST_JOB_INDEX = 4  # needed to select job posting for test

def inbox(request):
    recruiter = Recruiter.objects.get(id = RECRUITER_ID)
    threads = MessageThread.objects.filter(recruiter = recruiter).select_related('candidate', 'job')

    # Needed to match faiss index ids (check create_faiss_index func)
    threads = sorted(threads, key=lambda x: x.candidate.name, reverse=False)

    # Analyzator.convert_db_to_json()

    # Uncomment these lines to create new faiss index
    # if os.path.exists(faiss_index_path) is False:
    #    analyzator.create_faiss_index(threads, faiss_index_path)

    # Inbox based on recruiter-candidate communication
    # but we need to select job for candidates search
    selected_job = threads[TEST_THREAD_INDEX].job
    ####

    distances, indices = analyzator.faiss_search(selected_job, k=1000)

    threads = filter(lambda x: x.candidate_id in indices, threads)

    threads = map(lambda x:x[1], sorted(enumerate(threads), key=lambda x: distances[0][x[0]], reverse=False)) # sort threads by distance

    _context = { 'title': "Djinni - Inbox", 'recruiter': recruiter, 'threads': threads }

    return render(request, 'inbox/chats.html', _context)


def plot(request):
    print("computationally intensive process")

    all_jobs = JobPosting.objects.all()
    test_job = all_jobs[TEST_JOB_INDEX]

    job_threads = MessageThread.objects.filter(job=test_job)

    candidate_strs = []
    candidate_meta_text = []
    for th_index, thread in enumerate(job_threads):
        candidate_strs.append(analyzator.model_to_string(thread.candidate))
        candidate_meta_text.append(f"candidate: {thread.candidate.primary_keyword} <br>  min salary {thread.candidate.salary_min}")

    start_time = time.time()
    cand_embeddings = analyzator.hg_sentence_model.encode(candidate_strs, convert_to_tensor=True)
    job_embeddings = analyzator.hg_sentence_model.encode(analyzator.model_to_string(test_job), convert_to_tensor=True)
    print("exec time", time.time() - start_time)

    cand_pca, job_pca = analyzator.PCA(cand_embeddings, job_embeddings)

    pcas = np.concatenate([job_pca, cand_pca]) # job is first
    x = list(pcas[:, 0])
    y = list(pcas[:, 1])
    z = list(pcas[:, 2])

    colors = [[0, 255, 0]] + [[255, 0, 0]] * cand_pca.shape[0]

    meta_text = [f"Job: {test_job.position}"] + candidate_meta_text

    _context = { 'title': "Djinni - Plot", "x": x, "y": y, "z": z, "colors": colors, "meta_text":meta_text}

    return render(request, 'plots/plot.html', _context)

def inbox_thread(request, pk):
    thread = MessageThread.objects.get(id = pk)
    messages = thread.message_set.all().order_by('created')

    similarity = analyzator.get_candidate_job_similarity(thread)

    _context = {
        'pk': pk,
        'title': "Djinni - Inbox",
        'thread': thread,
        'messages': messages,
        'candidate': thread.candidate,
        'similarity': similarity,
    }

    return render(request, 'inbox/thread.html', _context)
