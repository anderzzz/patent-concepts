SELECT assignee_id, COUNT(assignee_id)
FROM patents_assignees GROUP BY assignee_id
ORDER BY COUNT(*) DESC;

SELECT * FROM patents_assignees t1
INNER JOIN assignees t2 ON t1.assignee_id = t2.assignee_id;

SELECT * FROM patents_assignees t1
INNER JOIN assignees t2 ON t1.assignee_id = t2.assignee_id
GROUP BY t1.assignee_id;


/*
Verify that all patents have concepts
*/
SELECT id FROM patents_subjects
WHERE id NOT IN (
    SELECT id FROM patents
);

/*
Count number of patent applications associated with
assignees and sort descending
 */
SELECT COUNT(*) TotalCount, t2.assignee_id, name
FROM patents_assignees t1
INNER JOIN assignees t2 ON t1.assignee_id = t2.assignee_id
GROUP BY t2.assignee_id
ORDER BY COUNT(*) DESC;

/*
Check days between patent publication dates. Sanity check
*/
SELECT diff_date FROM (
    SELECT publication_date, 
       JULIANDAY(publication_date) - 
       JULIANDAY((LAG(publication_date) OVER (ORDER BY publication_date ASC))) 
       AS diff_date
    FROM patents
)
GROUP BY diff_date;

/*
Extract concept counts for a given company and section
*/
SELECT concept, COUNT(concept) FROM patents_subjects
WHERE (sections LIKE '%claims%') AND id IN (
    SELECT patents_assignees.id FROM patents_assignees
    LEFT JOIN assignees
    ON patents_assignees.assignee_id = assignees.assignee_id
    WHERE assignees.name LIKE '%moderna%'
)
GROUP BY concept
ORDER BY COUNT(concept) DESC;

/*
Create fraction of concepts in various assignee''s patents in particular section
filtered by minimum number of patents in data set
*/
SELECT t3.assignee_id,
       t3.concept,
       t3.count_concepts,
       t2.total_p,
       CAST(t3.count_concepts AS FLOAT) / CAST(t2.total_p AS FLOAT) AS fraction
FROM (
    SELECT t1.assignee_id, t1.concept, COUNT(t1.concept) AS count_concepts
    FROM (
        SELECT patents_assignees.id, patents_assignees.assignee_id, cons.concept
        FROM (
            SELECT DISTINCT id, concept
            FROM patents_subjects
            WHERE sections LIKE '%claims%'
        ) AS cons
        LEFT OUTER JOIN patents_assignees
        ON cons.id = patents_assignees.id
    ) AS t1
    GROUP BY t1.assignee_id, t1.concept
) AS t3
INNER JOIN (
    SELECT assignee_id, COUNT(id) AS total_p
    FROM patents_assignees
    GROUP BY assignee_id
    HAVING COUNT(id) > 100
) AS t2
ON t3.assignee_id = t2.assignee_id
ORDER BY t2.total_p DESC, t3.count_concepts DESC;