-- ============================================================================
-- PostgreSQL tsvector Tutorial
-- ============================================================================
-- tsvector is PostgreSQL's data type for full-text search. It stores a sorted
-- list of distinct lexemes (normalized words) with optional position info.
--
-- Why use it?
--   1. Speed: GIN indexes enable fast lookups vs LIKE '%keyword%'
--   2. Linguistic smarts: Stemming means "running" matches "run", "runs", "ran"
--   3. Ranking: Score results by relevance with ts_rank()
--   4. Phrase search: Find words near each other, in order
-- ============================================================================


-- ============================================================================
-- PART 1: Understanding tsvector basics
-- ============================================================================

-- See what to_tsvector() produces
-- Notice: "The" removed (stop word), "foxes"→"fox", "jumped"→"jump", "quickly"→"quick"
SELECT to_tsvector('english', 'The quick brown foxes jumped over the lazy dogs quickly');
-- Result: 'brown':3 'dog':9 'fox':4 'jump':5 'lazi':8 'quick':2,10


-- The search counterpart: tsquery
SELECT to_tsquery('english', 'running');              -- stems to 'run'
SELECT to_tsquery('english', 'machine & learning');   -- AND
SELECT to_tsquery('english', 'dog | cat');            -- OR
SELECT to_tsquery('english', '!spam');                -- NOT
SELECT to_tsquery('english', 'machine <-> learning'); -- FOLLOWED BY (phrase)


-- ============================================================================
-- PART 2: Create sample data (100 articles)
-- ============================================================================

DROP TABLE IF EXISTS articles;

CREATE TABLE articles (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

INSERT INTO articles (title, body) VALUES
-- Tech articles
('Introduction to Machine Learning', 'Machine learning is a subset of artificial intelligence that enables computers to learn from data. Neural networks and deep learning have revolutionized how we approach complex problems.'),
('Building REST APIs with Python', 'Python is excellent for building RESTful APIs. Flask and FastAPI are popular frameworks. JSON responses and HTTP methods form the foundation of REST architecture.'),
('Docker Containers Explained', 'Docker containers provide lightweight virtualization. Images, containers, and volumes are core concepts. Kubernetes orchestrates containers at scale.'),
('PostgreSQL Performance Tuning', 'Database performance depends on proper indexing, query optimization, and configuration. EXPLAIN ANALYZE helps identify slow queries. Connection pooling reduces overhead.'),
('JavaScript Async Programming', 'Promises and async/await make asynchronous JavaScript readable. Event loops handle non-blocking operations. Callbacks were the original approach.'),
('Data Pipeline Best Practices', 'ETL processes extract, transform, and load data. Airflow schedules workflows. Data quality checks prevent downstream issues.'),
('Introduction to Kubernetes', 'Kubernetes manages containerized applications. Pods, services, and deployments are fundamental. Helm charts simplify configuration.'),
('SQL Query Optimization', 'Indexes speed up queries dramatically. Query plans reveal execution strategies. Proper joins and WHERE clauses improve performance.'),
('Git Version Control Basics', 'Git tracks changes in source code. Branches allow parallel development. Merging combines changes from different branches.'),
('Cloud Computing Overview', 'AWS, GCP, and Azure dominate cloud computing. Serverless functions reduce operational overhead. Object storage scales infinitely.'),

-- Science articles
('Climate Change Science', 'Global temperatures are rising due to greenhouse gas emissions. Carbon dioxide and methane trap heat in the atmosphere. Renewable energy offers solutions.'),
('Quantum Computing Fundamentals', 'Qubits can exist in superposition unlike classical bits. Quantum entanglement enables faster computation. Decoherence remains a major challenge.'),
('CRISPR Gene Editing', 'CRISPR allows precise DNA editing. Cas9 protein cuts genetic sequences. Medical applications include treating genetic diseases.'),
('The Human Microbiome', 'Trillions of bacteria live in our digestive system. Gut health affects mental health and immunity. Probiotics can restore bacterial balance.'),
('Space Exploration Updates', 'Mars missions seek signs of ancient life. SpaceX and NASA collaborate on rocket development. The James Webb telescope reveals distant galaxies.'),
('Renewable Energy Technologies', 'Solar panels convert sunlight to electricity. Wind turbines generate clean power. Battery storage addresses intermittency challenges.'),
('Artificial Neural Networks', 'Neural networks mimic brain structure. Layers of neurons process information. Backpropagation trains the network weights.'),
('Ocean Conservation Efforts', 'Plastic pollution threatens marine ecosystems. Coral reefs are dying from acidification. Marine protected areas help restore fish populations.'),
('Vaccine Development Process', 'Vaccines train the immune system to fight pathogens. Clinical trials test safety and efficacy. mRNA technology enabled rapid COVID vaccine development.'),
('Black Holes and Gravity', 'Black holes form when massive stars collapse. Event horizons mark the point of no return. Gravitational waves were detected for the first time in 2015.'),

-- Business articles
('Startup Funding Strategies', 'Venture capital provides growth funding for startups. Seed rounds typically raise one to five million dollars. Valuations depend on market potential.'),
('Remote Work Best Practices', 'Distributed teams require clear communication. Video calls enable face-to-face interaction. Documentation becomes critical without office presence.'),
('Digital Marketing Trends', 'Social media advertising reaches targeted audiences. SEO improves organic search visibility. Content marketing builds brand authority.'),
('Supply Chain Management', 'Just-in-time inventory reduces storage costs. Global supply chains face disruption risks. Logistics technology improves tracking.'),
('Financial Planning Basics', 'Diversification reduces investment risk. Compound interest grows wealth over time. Emergency funds provide financial security.'),
('Customer Experience Design', 'User research reveals customer needs. Journey mapping identifies pain points. Personalization improves satisfaction.'),
('Agile Project Management', 'Scrum organizes work into sprints. Daily standups maintain team alignment. Retrospectives drive continuous improvement.'),
('E-commerce Optimization', 'Shopping cart abandonment costs billions annually. Fast checkout reduces friction. Mobile optimization is essential.'),
('Leadership Development', 'Effective leaders inspire and empower teams. Emotional intelligence drives success. Feedback culture promotes growth.'),
('Sustainable Business Practices', 'ESG metrics measure environmental and social impact. Carbon neutrality targets drive change. Circular economy principles reduce waste.'),

-- Health articles
('Nutrition and Wellness', 'Balanced diets include proteins, carbohydrates, and fats. Vitamins and minerals support body functions. Hydration is often overlooked.'),
('Exercise and Mental Health', 'Physical activity releases endorphins. Regular exercise reduces anxiety and depression. Even walking provides benefits.'),
('Sleep Science', 'Adults need seven to nine hours of sleep. REM cycles are essential for memory consolidation. Blue light disrupts circadian rhythms.'),
('Stress Management Techniques', 'Meditation reduces cortisol levels. Deep breathing activates relaxation response. Time in nature improves mental health.'),
('Heart Health Guidelines', 'Cardiovascular disease is the leading cause of death. Diet and exercise prevent many cases. Blood pressure monitoring is important.'),
('Diabetes Prevention', 'Type 2 diabetes is largely preventable. Blood sugar control requires diet management. Regular screening detects early signs.'),
('Mental Health Awareness', 'Depression affects millions worldwide. Therapy and medication offer treatment options. Reducing stigma encourages seeking help.'),
('Allergies and Immune Response', 'Allergies result from immune system overreaction. Histamine causes typical allergy symptoms. Immunotherapy can reduce sensitivity.'),
('Bone Health and Osteoporosis', 'Calcium and vitamin D strengthen bones. Weight-bearing exercise builds bone density. Risk increases with age especially for women.'),
('Eye Care and Vision', 'Screen time causes digital eye strain. Regular eye exams detect problems early. UV protection prevents damage.'),

-- Culture and lifestyle
('Modern Architecture Trends', 'Sustainable building materials gain popularity. Open floor plans maximize natural light. Smart home technology integrates with design.'),
('Coffee Culture Worldwide', 'Ethiopia is the birthplace of coffee. Espresso originated in Italy. Third wave coffee emphasizes quality and origin.'),
('Travel Photography Tips', 'Golden hour provides the best natural lighting. Composition follows the rule of thirds. Editing enhances but should not distort.'),
('Urban Gardening Guide', 'Container gardens work on balconies. Vertical gardens maximize small spaces. Composting recycles organic waste.'),
('Podcast Production Basics', 'Quality microphones improve audio. Editing software removes mistakes. Consistent publishing builds audiences.'),
('Minimalist Living', 'Decluttering reduces stress and saves time. Quality over quantity guides purchases. Experiences matter more than possessions.'),
('Wine Tasting Fundamentals', 'Aroma reveals grape variety and aging. Tannins create texture in red wines. Temperature affects flavor perception.'),
('Hiking and Outdoor Recreation', 'Trail difficulty ratings guide planning. Leave no trace principles protect nature. Proper gear prevents injuries.'),
('Home Cooking Essentials', 'Sharp knives make cooking safer and easier. Cast iron pans last generations. Mise en place organizes prep work.'),
('Music Production Introduction', 'DAW software records and mixes audio. MIDI controllers input musical notes. Compression and EQ shape the sound.'),

-- Education
('Online Learning Strategies', 'Self-paced courses require discipline. Active recall improves retention. Note-taking enhances comprehension.'),
('Teaching Critical Thinking', 'Questioning assumptions develops analysis skills. Evidence evaluation prevents misinformation. Logical reasoning structures arguments.'),
('Language Learning Methods', 'Immersion accelerates fluency. Spaced repetition aids vocabulary retention. Speaking practice builds confidence.'),
('STEM Education Importance', 'Science literacy prepares students for modern careers. Hands-on experiments engage learners. Coding teaches computational thinking.'),
('Early Childhood Development', 'Play-based learning supports cognitive growth. Social interaction develops emotional skills. Reading to children builds language ability.'),

-- More tech
('Cybersecurity Fundamentals', 'Encryption protects data in transit. Two-factor authentication prevents unauthorized access. Regular updates patch vulnerabilities.'),
('Mobile App Development', 'React Native enables cross-platform development. User experience drives app success. App store optimization increases downloads.'),
('Big Data Analytics', 'Hadoop processes massive datasets. Data lakes store raw information. Business intelligence extracts insights.'),
('Blockchain Technology', 'Distributed ledgers ensure transparency. Smart contracts automate agreements. Cryptocurrency uses blockchain for transactions.'),
('Internet of Things', 'Connected devices generate massive data. Sensors monitor environments continuously. Edge computing processes data locally.'),

-- More science
('Evolutionary Biology', 'Natural selection drives species adaptation. Genetic mutations create variation. Fossil records document evolutionary history.'),
('Astronomy Basics', 'Stars form from collapsing gas clouds. Planets orbit in elliptical paths. Light years measure cosmic distances.'),
('Chemistry in Daily Life', 'Chemical reactions power cooking and cleaning. pH levels affect soil and skincare. Polymers make up most plastics.'),
('Psychology Research Methods', 'Controlled experiments establish causation. Surveys measure attitudes and beliefs. Longitudinal studies track changes over time.'),
('Environmental Science', 'Ecosystems depend on biodiversity. Pollution disrupts natural cycles. Conservation protects endangered species.'),

-- More business
('Negotiation Skills', 'Preparation determines negotiation outcomes. Active listening builds rapport. Win-win solutions create lasting agreements.'),
('Brand Strategy Development', 'Brand identity communicates values. Consistency builds recognition. Storytelling creates emotional connections.'),
('Data-Driven Decision Making', 'Analytics replace gut instinct. A/B testing validates hypotheses. Dashboards visualize key metrics.'),
('Innovation Management', 'Creative culture encourages experimentation. Failure is part of the innovation process. Customer feedback guides development.'),
('International Business', 'Cultural awareness prevents misunderstandings. Exchange rates affect profitability. Trade agreements shape market access.'),

-- More health
('Preventive Healthcare', 'Annual checkups catch problems early. Vaccinations prevent infectious diseases. Lifestyle choices impact long-term health.'),
('Physical Therapy Benefits', 'Rehabilitation restores mobility after injury. Stretching prevents muscle imbalances. Core strength supports posture.'),
('Nutrition for Athletes', 'Protein supports muscle recovery. Carbohydrates fuel endurance. Timing of meals affects performance.'),
('Dental Health Care', 'Brushing and flossing prevent cavities. Regular cleanings remove tartar. Gum disease links to heart problems.'),
('Skin Care Science', 'Sunscreen prevents premature aging. Retinoids increase cell turnover. Moisturizers maintain skin barrier.'),

-- More culture
('Film History Overview', 'Silent films pioneered cinematic techniques. Sound revolutionized storytelling. Digital effects transform modern movies.'),
('Contemporary Art Movements', 'Conceptual art prioritizes ideas over aesthetics. Installation art transforms spaces. Digital art challenges traditional boundaries.'),
('World Cuisine Exploration', 'Spices define regional cuisines. Fermentation creates unique flavors. Traditional techniques preserve culture.'),
('Fashion Industry Evolution', 'Fast fashion raises sustainability concerns. Vintage clothing gains popularity. Technology enables customization.'),
('Sports Analytics Revolution', 'Data transforms coaching strategies. Player tracking reveals performance patterns. Fantasy sports drive fan engagement.'),

-- More misc
('Personal Finance Management', 'Budgeting tracks income and expenses. Debt reduction frees future income. Retirement planning requires early start.'),
('Time Management Techniques', 'Prioritization focuses on important tasks. Pomodoro technique maintains focus. Calendar blocking protects productive time.'),
('Public Speaking Skills', 'Practice reduces presentation anxiety. Story structure engages audiences. Visual aids support key points.'),
('Writing Improvement Tips', 'Clear writing requires clear thinking. Editing improves every draft. Reading widely expands vocabulary.'),
('Networking Strategies', 'Genuine connections outlast transactional ones. Follow-up maintains relationships. Online presence complements in-person meetings.'),

-- Final batch
('Artificial Intelligence Ethics', 'AI bias reflects training data problems. Transparency builds trust. Regulation balances innovation and safety.'),
('Future of Work', 'Automation changes job requirements. Continuous learning becomes essential. Hybrid work balances flexibility and collaboration.'),
('Sustainable Living Guide', 'Reducing consumption has the biggest impact. Reusable products replace disposables. Local purchasing supports communities.'),
('Mental Models for Decision Making', 'First principles thinking breaks down problems. Inversion considers avoiding failure. Probabilistic thinking handles uncertainty.'),
('Creative Problem Solving', 'Brainstorming generates diverse ideas. Constraints often spark creativity. Iteration improves solutions.'),
('Meditation Practices', 'Mindfulness meditation focuses on present awareness. Breathing exercises calm the nervous system. Regular practice rewires brain patterns.'),
('Home Renovation Planning', 'Budget overruns are common in renovations. Permits ensure code compliance. Contractors should be licensed and insured.'),
('Pet Care Essentials', 'Regular veterinary checkups maintain pet health. Nutrition requirements vary by species. Exercise prevents behavioral problems.'),
('Photography Composition', 'Leading lines draw viewer attention. Negative space creates visual balance. Color theory enhances mood.'),
('Cooking Techniques', 'Searing creates flavorful crust through Maillard reaction. Braising tenderizes tough cuts. Emulsification combines oil and water.'),
('Investment Strategies', 'Index funds offer diversified exposure. Dollar cost averaging reduces timing risk. Long-term holding minimizes taxes.'),
('Gardening Basics', 'Soil health determines plant success. Companion planting benefits growth. Mulching retains moisture and suppresses weeds.'),
('History of the Internet', 'ARPANET was the precursor to the modern internet. Tim Berners-Lee invented the World Wide Web. Broadband enabled rich media streaming.'),
('Climate Adaptation Strategies', 'Rising sea levels threaten coastal communities. Infrastructure must be resilient to extreme weather. Agriculture adapts planting schedules.'),
('Emotional Intelligence', 'Self-awareness is the foundation of EQ. Empathy enables understanding others. Social skills build effective relationships.');

SELECT COUNT(*) AS article_count FROM articles;


-- ============================================================================
-- PART 3: Basic full-text search (without stored column)
-- ============================================================================

-- Search for articles about "machine learning" using @@ operator
SELECT id, title 
FROM articles 
WHERE to_tsvector('english', title || ' ' || body) @@ to_tsquery('english', 'machine & learning');


-- Search showing stemming: "database" matches "databases"
SELECT id, title 
FROM articles 
WHERE to_tsvector('english', title || ' ' || body) @@ to_tsquery('english', 'database');


-- ============================================================================
-- PART 4: Add stored tsvector column with weights + GIN index
-- ============================================================================

-- Add column to store pre-computed tsvector
ALTER TABLE articles ADD COLUMN search_vector tsvector;

-- Populate with weighted fields (A = title, B = body)
-- Weight A is highest priority, D is lowest
UPDATE articles SET search_vector = 
    setweight(to_tsvector('english', coalesce(title, '')), 'A') ||
    setweight(to_tsvector('english', coalesce(body, '')), 'B');

-- Create GIN index for fast lookups
CREATE INDEX idx_articles_search ON articles USING GIN(search_vector);

-- See what the stored vector looks like
SELECT id, title, search_vector 
FROM articles 
WHERE id = 1;


-- ============================================================================
-- PART 5: Search with ranking
-- ============================================================================

-- ts_rank scores relevance - title matches (weight A) rank higher
-- this query is finding the most relevant rows w/ the word learning and using those weights in search_vector to help find that?
SELECT 
    id,
    title,
    ts_rank(search_vector, query) AS rank
FROM articles, to_tsquery('english', 'learning') AS query
WHERE search_vector @@ query
ORDER BY rank DESC
LIMIT 10;


-- Phrase search: find "neural networks" as adjacent words
-- The <-> operator means "followed by"—it finds rows where "neural" appears immediately before "network" (adjacent words).
-- it matcheds "Neural networks are powerful", but not "neural and network" (word in between)"
SELECT id, title
FROM articles
WHERE search_vector @@ to_tsquery('english', 'neural <-> network');


-- ============================================================================
-- PART 6: Headline generation (highlighted snippets)
-- ============================================================================

SELECT 
    id,
    title,
    ts_headline('english', body, to_tsquery('english', 'climate & carbon'), 
        'StartSel=<<, StopSel=>>, MaxWords=35, MinWords=15') AS headline
FROM articles
WHERE search_vector @@ to_tsquery('english', 'climate & carbon');


-- ============================================================================
-- PART 7: websearch_to_tsquery - user-friendly query parsing
-- ============================================================================

-- Handles natural search syntax: quotes for phrases, OR, minus for exclusion
SELECT websearch_to_tsquery('english', '"machine learning" -spam');
SELECT websearch_to_tsquery('english', 'data pipeline OR etl');
SELECT websearch_to_tsquery('english', 'kubernetes containers deployment');

-- Practical search endpoint example
SELECT 
    id,
    title,
    ts_rank(search_vector, query) AS relevance
FROM articles, websearch_to_tsquery('english', 'python REST API') AS query
WHERE search_vector @@ query
ORDER BY relevance DESC
LIMIT 5;


-- ============================================================================
-- PART 8: Performance comparison (LIKE vs tsvector)
-- ============================================================================

-- LIKE approach: sequential scan, checks every row
EXPLAIN ANALYZE 
SELECT id, title FROM articles 
WHERE body ILIKE '%machine%' AND body ILIKE '%learning%';

-- tsvector approach: uses GIN index (force it for small tables)
SET enable_seqscan = off;
EXPLAIN ANALYZE 
SELECT id, title FROM articles 
WHERE search_vector @@ to_tsquery('english', 'machine & learning');
SET enable_seqscan = on;


-- ============================================================================
-- PART 9: Auto-update trigger
-- ============================================================================

-- Function to update search_vector on insert/update
CREATE OR REPLACE FUNCTION articles_search_trigger() RETURNS trigger AS $$
BEGIN
    NEW.search_vector :=
        setweight(to_tsvector('english', coalesce(NEW.title, '')), 'A') ||
        setweight(to_tsvector('english', coalesce(NEW.body, '')), 'B');
    RETURN NEW;
END
$$ LANGUAGE plpgsql;

-- Attach trigger to table
CREATE TRIGGER tsvector_update 
    BEFORE INSERT OR UPDATE ON articles 
    FOR EACH ROW EXECUTE FUNCTION articles_search_trigger();

-- Test it
INSERT INTO articles (title, body) 
VALUES ('Testing the Trigger', 'This article about PostgreSQL full text search should auto-index.');

SELECT id, title, search_vector 
FROM articles 
WHERE title = 'Testing the Trigger';


-- ============================================================================
-- PART 10: Additional useful queries
-- ============================================================================

-- Find articles matching ANY of multiple terms
SELECT id, title
FROM articles
WHERE search_vector @@ to_tsquery('english', 'docker | kubernetes | containers')
ORDER BY ts_rank(search_vector, to_tsquery('english', 'docker | kubernetes | containers')) DESC
LIMIT 5;

-- Prefix search (autocomplete-style)
SELECT id, title
FROM articles
WHERE search_vector @@ to_tsquery('english', 'mach:*');  -- matches machine, machining, etc.

-- Negation: articles about data but NOT machine learning
SELECT id, title
FROM articles
WHERE search_vector @@ to_tsquery('english', 'data & !machine')
LIMIT 5;

-- Combined ranking with cover density (rewards clustering of matches)
SELECT 
    id,
    title,
    ts_rank_cd(search_vector, query) AS rank_cd
FROM articles, to_tsquery('english', 'data & pipeline') AS query
WHERE search_vector @@ query
ORDER BY rank_cd DESC
LIMIT 5;


-- ============================================================================
-- SUMMARY
-- ============================================================================
-- 
-- | Function/Operator       | Purpose                                          |
-- |-------------------------|--------------------------------------------------|
-- | to_tsvector()           | Convert text → normalized lexemes with positions |
-- | to_tsquery()            | Create search query with &, |, !, <->            |
-- | websearch_to_tsquery()  | User-friendly parsing (quotes, OR, -)            |
-- | @@                      | Match tsvector against tsquery                   |
-- | ts_rank()               | Score relevance                                  |
-- | ts_rank_cd()            | Score with cover density (clustering bonus)      |
-- | ts_headline()           | Generate snippets with highlighted matches       |
-- | setweight()             | Assign importance (A > B > C > D)                |
-- | GIN index               | Fast lookups on large tables                     |
--
-- ============================================================================