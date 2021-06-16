/*
The following three tables define the patents, assignees, and inventors tables, which make no
reference to other tables.
*/
CREATE TABLE patents (
    id VARCHAR(32) PRIMARY KEY,
    title TEXT NOT NULL,
    priority_date DATE,
    filing_date DATE,
    publication_date DATE NOT NULL,
    grant_date DATE,
    result_link VARCHAR(50) NOT NULL
);

CREATE TABLE assignees (
    assignee_id INT,
    name VARCHAR(256),
    PRIMARY KEY(assignee_id)
);

CREATE TABLE inventors (
    inventor_id INT,
    name VARCHAR(256),
    PRIMARY KEY(inventor_id)
);

/*
The next two tables define mappings between patents and assignees, and patents and inventors.
Therefore the tables references two foreign keys from other tables. Note however that due to
nested assignments or inventors with identical names, every pair of such foreign keys are
not necessarily unique (though mostly true).
*/
CREATE TABLE patents_inventors (
    id VARCHAR(32),
    inventor_id INT,
    FOREIGN KEY(id) REFERENCES patents(id) ON DELETE CASCADE,
    FOREIGN KEY(inventor_id) REFERENCES inventors(inventor_id) ON DELETE CASCADE
);

CREATE TABLE patents_assignees (
    id VARCHAR(32),
    assignee_id INT,
    FOREIGN KEY(id) REFERENCES patents(id) ON DELETE CASCADE,
    FOREIGN KEY(assignee_id) REFERENCES assignees(assignee_id) ON DELETE CASCADE
);

/*
The table that associates a patent id with a plurality of concepts. Once populated it will be the largest
since each patent can be associated with hundres of concepts
*/
CREATE TABLE patents_subjects (
    id VARCHAR(32) NOT NULL,
    concept VARCHAR(256),
    domain VARCHAR(256) NOT NULL,
    inchi_key VARCHAR(27),
    smiles TEXT,
    sections VARCHAR(256) NOT NULL
);