def exp_years_to_float(years: str) -> float:
    if years == "no_exp":
        return 0
    else:
        return float([*years][0])
    

def score_english_level(level: str) -> int:
    if level == "basic":
        return 1
    elif level == "pre":
        return 2
    elif level == "intermediate":
        return 3
    elif level == "upper":
        return 4
    elif level == "fluent":
        return 5
    return 0


def count_score(model, lazy=False) -> int:
    score = 100
    candidate = model.candidate
    job = model.job
    
    if lazy:
        if candidate.country_code != "UKR" and job.is_ukraine_only:
            return 0
        if not candidate.can_relocate and job.relocate_type == "no_relocate" \
            and (job.remote_type == "office" or job.remote_type == "partly_remote"):
            return 0
        if candidate.salary_min > job.salary_min:
            score -= 10
        if candidate.employment != "parttime" and job.is_parttime:
            score -= 10
        if candidate.experience_years < exp_years_to_float(job.exp_years):
            score -= 20
        if score_english_level(candidate.english_level) < score_english_level(job.english_level):
            score -= 10
        if job.requires_cover_letter:
            if model.first_message.action == "apply" and len(model.first_message.body) < 1:
                score -= 50
    else:
        ...
            
    return score