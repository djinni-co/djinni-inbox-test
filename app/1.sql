SELECT jp.id, jp.position, count(mt.*)
FROM sandbox_messagethread mt
JOIN sandbox_jobposting jp ON mt.job_id = jp.id
GROUP BY jp.id
ORDER BY jp.id;

--    id   |            position             | count 
-- --------+---------------------------------+-------
--  534865 | Junior Front-End Engineer       |   688
--  541927 | Junior Back-End Engineer        |   130
--  550484 | Head of Media Buying            |    51
--  551065 | Junior/Middle Back-End Engineer |   105
--  556394 | Data Analyst                    |    64
--  566990 | Junior Data Analyst             |    79
--  569637 | Marketing Manager               |    21
--  577164 | Junior Front-End Engineer       |   917
--  577166 | Junior Back-End Engineer        |   159
--  582830 | Data Analyst                    |   106

-- ----------

SELECT jp.id, jp.position, count(mt.*)
FROM sandbox_messagethread mt
JOIN sandbox_jobposting jp ON mt.job_id = jp.id

WHERE mt.candidate_archived = False

GROUP BY jp.id
ORDER BY jp.id;

--    id   |            position             | count 
-- --------+---------------------------------+-------
--  534865 | Junior Front-End Engineer       |   686
--  541927 | Junior Back-End Engineer        |   113
--  550484 | Head of Media Buying            |    48
--  551065 | Junior/Middle Back-End Engineer |    97
--  556394 | Data Analyst                    |    62
--  566990 | Junior Data Analyst             |    54
--  569637 | Marketing Manager               |    18
--  577164 | Junior Front-End Engineer       |   787
--  577166 | Junior Back-End Engineer        |   145
--  582830 | Data Analyst                    |    82

-- ==============================================================

SELECT mt.job_id,
  MIN(jp.salary_min) AS jm_sal,
  MIN(jp.salary_max) AS jx_sal,
  MIN(cand.salary_min) AS am_sal,
  MAX(cand.salary_min) AS ax_sal,

  MIN(jp.exp_years) AS j_exp,
  MIN(cand.experience_years) AS am_exp,
  MAX(cand.experience_years) AS ax_exp,

  jp.position AS job_position

FROM  sandbox_messagethread mt
JOIN  sandbox_candidate cand ON mt.candidate_id = cand.id
JOIN  sandbox_jobposting jp ON mt.job_id = jp.id

GROUP BY mt.job_id, jp.position
ORDER BY mt.job_id;

--  job_id | jm_sal | jx_sal | am_sal | ax_sal | j_exp  | am_exp | ax_exp |          job_position           
-- --------+--------+--------+--------+--------+--------+--------+--------+---------------------------------
--  534865 |      1 |   2000 |    100 |   3300 | no_exp |      0 |     11 | Junior Front-End Engineer
--  541927 |      1 |   2000 |    150 |   6500 | no_exp |      0 |     11 | Junior Back-End Engineer
--  550484 |      1 |   4000 |   1000 |  15000 | 2y     |    1.5 |     11 | Head of Media Buying
--  551065 |      1 |   3000 |    200 |   6000 | no_exp |      0 |      6 | Junior/Middle Back-End Engineer
--  556394 |      1 |   3000 |    100 |   4000 | 1y     |      0 |      8 | Data Analyst
--  566990 |      1 |   2000 |    300 |   3000 | 1y     |      0 |     11 | Junior Data Analyst
--  569637 |      1 |   3000 |    700 |   3400 | 1y     |      1 |     11 | Marketing Manager
--  577164 |      1 |   2000 |    100 |   3500 | 1y     |      0 |     11 | Junior Front-End Engineer
--  577166 |      1 |   2000 |    300 |   5000 | 1y     |      0 |     10 | Junior Back-End Engineer
--  582830 |      1 |   2500 |    300 |   4000 | 1y     |      0 |     11 | Data Analyst

-- ----------

SELECT mt.job_id,
  MIN(jp.salary_min) AS jm_sal,
  MIN(jp.salary_max) AS jx_sal,
  MIN(cand.salary_min) AS am_sal,
  MAX(cand.salary_min) AS ax_sal,

  MIN(jp.exp_years) AS j_exp,
  MIN(cand.experience_years) AS am_exp,
  MAX(cand.experience_years) AS ax_exp,

  jp.position AS job_position

FROM sandbox_messagethread mt
JOIN sandbox_candidate cand ON mt.candidate_id = cand.id
JOIN sandbox_jobposting jp ON mt.job_id = jp.id

WHERE mt.candidate_archived = False

GROUP BY mt.job_id, jp.position
ORDER BY mt.job_id;

-- job_id | jm_sal | jx_sal | am_sal | ax_sal | j_exp  | am_exp | ax_exp |          job_position           
-- --------+--------+--------+--------+--------+--------+--------+--------+---------------------------------
--  534865 |      1 |   2000 |    100 |   3300 | no_exp |      0 |     11 | Junior Front-End Engineer
--  541927 |      1 |   2000 |    150 |   6500 | no_exp |      0 |     11 | Junior Back-End Engineer
-->  550484 |      1 |   4000 |   1000 |  15000 | 2y     |    1.5 |     11 | Head of Media Buying
--  551065 |      1 |   3000 |    200 |   6000 | no_exp |      0 |      6 | Junior/Middle Back-End Engineer
-->  556394 |      1 |   3000 |    100 |   4000 | 1y     |      0 |      8 | Data Analyst
--  566990 |      1 |   2000 |    300 |   2000 | 1y     |      0 |     10 | Junior Data Analyst
--  569637 |      1 |   3000 |    700 |   3400 | 1y     |      1 |     11 | Marketing Manager
--  577164 |      1 |   2000 |    100 |   3500 | 1y     |      0 |     11 | Junior Front-End Engineer
--  577166 |      1 |   2000 |    300 |   5000 | 1y     |      0 |     10 | Junior Back-End Engineer
--  582830 |      1 |   2500 |    300 |   3500 | 1y     |      0 |      7 | Data Analyst

-- ==============================================================

\set sal_weight 0.25
\set exp_weight 0.5

\set job_id  550484
\set exp_min 2::float
\set exp_max 11::float
\set sal_min 1000::float
\set sal_max 4000::float

\set exp_min 1.5::float
\set sal_max 15000::float

-- ----------

\set job_id  556394
\set exp_min 1::float
\set exp_max 8::float
\set sal_min 100::float
\set sal_max 3000::float

\set exp_min 0::float
\set sal_max 4000::float

-- ----------

\set exp_range (:exp_max - :exp_min)::float
\set sal_range (:sal_max - :sal_min)::float

SELECT mt.id, job_id, candidate_id,
  ROUND((
    (cand.experience_years - :exp_min)/:exp_range
  )::numeric, 5) AS exp_score,

  ROUND((
    (cand.salary_min - :sal_min)/:sal_range
  )::numeric, 5) AS sal_score,

  ROUND((
      :exp_weight * (cand.experience_years - :exp_min)/:exp_range
    - :sal_weight * (cand.salary_min - :sal_min)/:sal_range
  )::numeric, 5) AS total_score,

  cand.experience_years AS c_exp,
  cand.salary_min AS c_sal

FROM sandbox_messagethread mt
JOIN sandbox_candidate cand ON mt.candidate_id = cand.id
JOIN sandbox_jobposting jp ON mt.job_id = jp.id

WHERE job_id = :job_id
ORDER BY total_score;
