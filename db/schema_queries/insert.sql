
INSERT INTO users(id, name, surname, email, plan) 
VALUES ('bd35d25a-be7e-4f82-b68f-02ee8a9e61fd', 'John', 'Smith', 'john.smith@example.com',  'freemium'), 
    ('b04fb2c6-30d3-469e-b6d2-ad1e480c67a4', 'Jane', 'Smith', 'jane.smith@example.com', 'premium'), 
    ('d8c3cebc-c225-43f1-a2fe-e0cccd872ad7', 'Alex', 'Smith', 'alex.smith@example.com', 'gold');


INSERT INTO portfolios(type, user_id) 
VALUES ('stock', 'bd35d25a-be7e-4f82-b68f-02ee8a9e61fd'),
    ('crypto', 'bd35d25a-be7e-4f82-b68f-02ee8a9e61fd'),
    ('etf', 'b04fb2c6-30d3-469e-b6d2-ad1e480c67a4'),
    ('stock', 'b04fb2c6-30d3-469e-b6d2-ad1e480c67a4'),
    ('crypto', 'b04fb2c6-30d3-469e-b6d2-ad1e480c67a4'),
    ('crypto', 'd8c3cebc-c225-43f1-a2fe-e0cccd872ad7');