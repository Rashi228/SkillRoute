import sys
import os
sys.path.append('d:/HCL_Tech/backend')
from database import SessionLocal
from models import Skill
import json

db = SessionLocal()

skills_data = [
    # AI / ML
    ("Machine Learning", "Algorithms and statistical models that systems use to perform tasks without explicit instructions.", ["ML", "Predictive Modeling"]),
    ("Deep Learning", "Neural networks with multiple layers for learning complex patterns.", ["Neural Networks", "DNN", "CNN", "RNN"]),
    ("Generative AI", "AI that can create new content like text, images, and code.", ["GenAI"]),
    ("Large Language Models", "Deep learning algorithms that can recognize, summarize, translate, predict and generate text.", ["LLMs", "LLM", "GPT"]),
    ("Retrieval-Augmented Generation", "A technique combining information retrieval with generative language models.", ["RAG", "Retrieval Augmented Generation", "RAG systems"]),
    ("Natural Language Processing", "Interactions between computers and human language.", ["NLP", "Computational Linguistics", "Text Analytics"]),
    ("Computer Vision", "Deriving meaningful information from digital images and videos.", ["CV", "Image Processing", "Object Detection"]),
    ("MLOps", "Practices that aim to deploy and maintain machine learning models in production reliably.", ["Machine Learning Operations", "Model Deployment"]),
    ("Reinforcement Learning", "Training machine learning models to make a sequence of decisions.", ["RL"]),
    ("Prompt Engineering", "Designing and refining inputs to guide generative AI models.", ["Prompts", "LLM Prompting"]),
    
    # Software Engineering
    ("Data Structures", "Specialized formats for organizing, processing, retrieving and storing data.", ["Data Types", "Arrays", "Trees", "Graphs", "Linked Lists"]),
    ("Algorithms", "A finite sequence of rigorous instructions used to solve a class of specific problems.", ["Sorting", "Searching", "Dynamic Programming"]),
    ("System Design", "The process of defining the architecture, components, and interfaces for a system.", ["Architecture", "Scalability", "High Availability"]),
    ("Microservices", "An architectural style that structures an application as a collection of services.", ["Microservices Architecture"]),
    ("Object-Oriented Programming", "A programming paradigm based on the concept of objects.", ["OOP", "Object Oriented Design"]),
    ("Functional Programming", "A programming paradigm where programs are constructed by applying and composing functions.", ["FP"]),
    ("Test-Driven Development", "A software development process relying on software requirements being converted to test cases before software is fully developed.", ["TDD", "Unit Testing", "Integration Testing"]),
    
    # Backend
    ("Backend Development", "Server-side web development focused on databases, scripting, and website architecture.", ["Server-side", "Backend"]),
    ("API Design", "The process of developing application programming interfaces.", ["REST APIs", "GraphQL", "gRPC"]),
    ("Python", "High-level, general-purpose programming language.", ["Python 3", "Py"]),
    ("Node.js", "Cross-platform JavaScript runtime environment.", ["Node", "Express.js"]),
    ("Java", "High-level, class-based, object-oriented programming language.", ["Java SE", "Java EE", "Spring Boot"]),
    ("Go", "Statically typed, compiled programming language designed at Google.", ["Golang", "Go language"]),
    ("C++", "General-purpose programming language created as an extension of C.", ["C/C++", "CPP"]),
    ("Ruby on Rails", "Server-side web application framework written in Ruby.", ["Rails", "Ruby"]),
    
    # Frontend
    ("Frontend Development", "Development of the graphical user interface of a website.", ["UI Development", "Client-side"]),
    ("HTML/CSS", "Markup and styling languages for creating web pages.", ["HTML5", "CSS3", "Web Design"]),
    ("JavaScript", "High-level, often just-in-time compiled language that conforms to the ECMAScript standard.", ["JS", "ECMAScript", "ES6"]),
    ("React", "A declarative, efficient, and flexible JavaScript library for building user interfaces.", ["React.js", "ReactJS"]),
    ("Angular", "A TypeScript-based open-source web application framework.", ["AngularJS", "Angular 2+"]),
    ("Vue.js", "An open-source model–view–viewmodel front end JavaScript framework.", ["Vue", "VueJS"]),
    ("TypeScript", "A strict syntactical superset of JavaScript.", ["TS"]),
    
    # Cloud & DevOps
    ("Cloud Computing", "Delivery of computing services over the internet.", ["Cloud Architecture", "Cloud Migration"]),
    ("Amazon Web Services", "Comprehensive and broadly adopted cloud platform.", ["AWS", "Amazon Cloud"]),
    ("Microsoft Azure", "Cloud computing service operated by Microsoft.", ["Azure"]),
    ("Google Cloud Platform", "Suite of cloud computing services offered by Google.", ["GCP", "Google Cloud"]),
    ("DevOps", "A set of practices that combines software development and IT operations.", ["DevSecOps"]),
    ("Continuous Integration and Delivery", "Method to frequently deliver apps to customers by introducing automation.", ["CI/CD", "Continuous Deployment", "Jenkins", "GitHub Actions"]),
    ("Docker", "Platform for developing, shipping, and running applications in containers.", ["Containerization", "Containers"]),
    ("Kubernetes", "Open-source system for automating deployment, scaling, and management of containerized applications.", ["K8s", "Container Orchestration"]),
    ("Infrastructure as Code", "The process of managing and provisioning computer data centers through machine-readable definition files.", ["IaC", "Terraform", "Ansible"]),
    
    # Data & Database
    ("Database Management", "Storing, retrieving and managing data in databases.", ["Databases", "DBMS"]),
    ("SQL", "Domain-specific language used in programming and designed for managing data held in a relational database management system.", ["Relational Databases", "MySQL", "PostgreSQL"]),
    ("NoSQL", "Database provides a mechanism for storage and retrieval of data that is modeled in means other than the tabular relations.", ["MongoDB", "Document Databases", "Key-Value Stores"]),
    ("Data Engineering", "The design and building of systems for collecting, storing, and analyzing data at scale.", ["Data Pipelines", "ETL"]),
    ("Big Data", "Large and complex data sets that are difficult to process using traditional data processing applications.", ["Hadoop", "Spark", "Data Lakes"]),
    ("Data Science", "Extracting knowledge and insights from data using statistics and machine learning.", ["Data Analysis", "Data Analytics"]),
    
    # Security
    ("Cybersecurity", "Protecting computer systems and networks from information disclosure and damage.", ["Information Security", "Infosec"]),
    ("Network Security", "Protection of the access to files and directories in a computer network.", ["Firewalls", "VPNs"]),
    ("Cryptography", "Practice and study of techniques for secure communication.", ["Encryption", "Hashing", "PKI"]),
    
    # Others
    ("Agile Methodology", "A practice that promotes continuous iteration of development and testing throughout the software development lifecycle.", ["Agile", "Scrum", "Kanban"]),
    ("UI/UX Design", "Designing user interfaces and user experiences for machines and software.", ["User Experience", "User Interface", "Figma"]),
    ("Mobile Development", "The process of creating software applications that run on a mobile device.", ["iOS", "Android", "React Native", "Flutter"]),
    ("Blockchain", "A growing list of records, called blocks, that are securely linked together using cryptography.", ["Web3", "Smart Contracts", "Cryptocurrency"])
]

count = 0
for name, desc, aliases in skills_data:
    existing = db.query(Skill).filter(Skill.name == name).first()
    if not existing:
        db.add(Skill(name=name, description=desc, aliases=json.dumps(aliases)))
        count += 1
    else:
        existing.description = desc
        existing.aliases = json.dumps(aliases)

db.commit()
print(f'Successfully added or updated {len(skills_data)} explicit skills (New: {count}).')
