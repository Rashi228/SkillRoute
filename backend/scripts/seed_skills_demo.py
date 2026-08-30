import os
import sys
import json

# Add backend directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models import Skill

def seed_skills():
    db = SessionLocal()
    
    # Check current count
    initial_count = db.query(Skill).count()
    print(f"Initial Skill count: {initial_count}")
    
    skills_data = [
        # AI / Machine Learning
        {"name": "Artificial Intelligence", "desc": "The simulation of human intelligence in machines.", "aliases": ["AI", "Artificial Intel", "AI Engineering"]},
        {"name": "Machine Learning", "desc": "Algorithms that improve automatically through experience.", "aliases": ["ML", "Machine Learning Engineering", "ML Engineering"]},
        {"name": "Deep Learning", "desc": "A subset of ML based on artificial neural networks.", "aliases": ["DL", "Deep Neural Networks"]},
        {"name": "Neural Networks", "desc": "Computing systems inspired by biological neural networks.", "aliases": ["ANN", "Artificial Neural Networks"]},
        {"name": "Natural Language Processing", "desc": "Interactions between computers and human language.", "aliases": ["NLP", "Computational Linguistics", "Language Processing"]},
        {"name": "Computer Vision", "desc": "How computers can gain understanding from images or video.", "aliases": ["CV", "Machine Vision"]},
        {"name": "Generative AI", "desc": "AI capable of generating text, images, or other media.", "aliases": ["GenAI", "Generative Artificial Intelligence"]},
        {"name": "Large Language Models", "desc": "Advanced AI models trained on vast amounts of text data.", "aliases": ["LLM", "LLMs", "Large Language Model"]},
        {"name": "Transformers", "desc": "A deep learning architecture based on self-attention mechanisms.", "aliases": ["Transformer Models", "Attention Mechanisms"]},
        {"name": "Retrieval-Augmented Generation", "desc": "Optimizing LLMs using external knowledge bases.", "aliases": ["RAG", "Retrieval Augmented Generation", "RAG Systems", "Production RAG"]},
        {"name": "Prompt Engineering", "desc": "The practice of designing inputs for AI models.", "aliases": ["Prompting", "AI Prompting"]},
        {"name": "AI Agents", "desc": "Autonomous systems that perceive environments and act.", "aliases": ["Autonomous Agents", "Agentic AI", "AI Assistants"]},
        {"name": "Model Evaluation", "desc": "Assessing the performance of machine learning models.", "aliases": ["Model Testing", "Evaluation Metrics"]},
        {"name": "MLOps", "desc": "Machine Learning Operations for managing ML lifecycles.", "aliases": ["ML Ops", "Machine Learning Operations"]},
        {"name": "Fine Tuning", "desc": "Taking a pre-trained model and training it further.", "aliases": ["Model Fine-tuning", "Transfer Learning"]},
        {"name": "Vector Databases", "desc": "Databases optimized for storing and querying vector embeddings.", "aliases": ["Vector Search", "Vector DBs", "Pinecone", "Milvus"]},
        {"name": "Embeddings", "desc": "Mathematical representations of text or data.", "aliases": ["Vector Embeddings", "Text Embeddings", "Semantic Embeddings"]},
        
        # Software Engineering
        {"name": "Programming Fundamentals", "desc": "Core concepts of computer programming.", "aliases": ["Coding Basics", "Programming Basics", "Intro to Programming"]},
        {"name": "Data Structures", "desc": "Data organization, management, and storage formats.", "aliases": ["DSA", "Data Structures and Algorithms"]},
        {"name": "Algorithms", "desc": "Step-by-step procedures for calculations.", "aliases": ["Algorithm Design", "Sorting and Searching"]},
        {"name": "Object-Oriented Programming", "desc": "Programming paradigm based on the concept of objects.", "aliases": ["OOP", "Object Oriented Design"]},
        {"name": "Design Patterns", "desc": "Typical solutions to common problems in software design.", "aliases": ["Software Design Patterns", "GoF Patterns"]},
        {"name": "System Design", "desc": "Defining architecture, components, and modules.", "aliases": ["Systems Architecture", "Scalable Systems"]},
        {"name": "Software Architecture", "desc": "High-level structures of a software system.", "aliases": ["App Architecture", "Software Engineering Architecture"]},
        {"name": "Distributed Systems", "desc": "Systems whose components are located on different networked computers.", "aliases": ["Distributed Computing"]},
        {"name": "Software Testing", "desc": "Evaluating software to identify bugs and issues.", "aliases": ["QA", "Quality Assurance", "Testing"]},
        {"name": "Unit Testing", "desc": "Testing individual units or components of a software.", "aliases": ["TDD", "Test-Driven Development"]},
        {"name": "Integration Testing", "desc": "Testing combined parts of an application.", "aliases": ["System Integration Testing"]},
        {"name": "API Design", "desc": "Process of developing Application Programming Interfaces.", "aliases": ["REST API Design", "API Development"]},
        {"name": "Git", "desc": "Distributed version control system.", "aliases": ["Version Control", "Source Control"]},
        {"name": "GitHub", "desc": "Platform for version control and collaboration.", "aliases": ["GitLab", "Bitbucket", "Git Hosting"]},
        
        # Backend
        {"name": "Backend Development", "desc": "Server-side web development.", "aliases": ["Backend", "Backend Engineering", "Server-Side Development", "Server Development"]},
        {"name": "Python", "desc": "High-level, general-purpose programming language.", "aliases": ["Python Programming", "Python 3"]},
        {"name": "FastAPI", "desc": "Modern, fast web framework for building APIs with Python.", "aliases": ["Fast API"]},
        {"name": "Django", "desc": "High-level Python web framework.", "aliases": ["Django Framework"]},
        {"name": "Flask", "desc": "Micro web framework written in Python.", "aliases": ["Flask Framework"]},
        {"name": "Node.js", "desc": "JavaScript runtime environment.", "aliases": ["Node", "NodeJS"]},
        {"name": "Express.js", "desc": "Web application framework for Node.js.", "aliases": ["Express", "Express JS"]},
        {"name": "REST APIs", "desc": "Representational state transfer APIs.", "aliases": ["RESTful APIs", "REST Architecture"]},
        {"name": "GraphQL", "desc": "Query language for APIs.", "aliases": ["Graph QL"]},
        {"name": "Authentication", "desc": "Process of verifying user identity.", "aliases": ["Auth", "User Authentication", "Login Systems"]},
        {"name": "JWT", "desc": "JSON Web Tokens.", "aliases": ["JSON Web Token", "Bearer Tokens"]},
        {"name": "Microservices", "desc": "Architectural style structuring an application as a collection of services.", "aliases": ["Microservices Architecture", "Microservice"]},
        {"name": "Database Management", "desc": "Administration of database systems.", "aliases": ["Databases", "DB Management", "DBMS"]},
        {"name": "PostgreSQL", "desc": "Open source object-relational database system.", "aliases": ["Postgres", "PostgreSQL Database"]},
        {"name": "Redis", "desc": "In-memory data structure store.", "aliases": ["Redis Cache", "In-Memory Caching"]},
        {"name": "Message Queues", "desc": "Asynchronous service-to-service communication.", "aliases": ["Kafka", "RabbitMQ", "Event Driven Architecture"]},
        
        # Frontend
        {"name": "Frontend Development", "desc": "Development of the graphical user interface.", "aliases": ["Frontend", "Front-end Engineering", "UI Development", "Web Development"]},
        {"name": "HTML/CSS", "desc": "Core technologies for building Web pages.", "aliases": ["HTML", "CSS", "Web Design"]},
        {"name": "JavaScript", "desc": "Programming language of the Web.", "aliases": ["JS", "Vanilla JS", "ECMAScript"]},
        {"name": "TypeScript", "desc": "Strict syntactical superset of JavaScript.", "aliases": ["TS", "Type Script"]},
        {"name": "React", "desc": "JavaScript library for building user interfaces.", "aliases": ["ReactJS", "React.js"]},
        {"name": "Next.js", "desc": "React framework for production.", "aliases": ["NextJS", "Next.js Framework"]},
        {"name": "Angular", "desc": "TypeScript-based web application framework.", "aliases": ["AngularJS", "Angular Framework"]},
        {"name": "Vue.js", "desc": "Progressive JavaScript framework.", "aliases": ["Vue", "VueJS"]},
        {"name": "Tailwind CSS", "desc": "Utility-first CSS framework.", "aliases": ["Tailwind", "Utility CSS"]},
        {"name": "Web Accessibility", "desc": "Designing websites for people with disabilities.", "aliases": ["a11y", "Accessibility"]},
        {"name": "State Management", "desc": "Managing state of a user interface.", "aliases": ["Redux", "Zustand", "Context API"]},
        
        # Data
        {"name": "SQL", "desc": "Structured Query Language.", "aliases": ["SQL Queries", "Relational Databases"]},
        {"name": "Data Analysis", "desc": "Inspecting, cleansing, and modeling data.", "aliases": ["Data Analytics", "Exploratory Data Analysis"]},
        {"name": "Pandas", "desc": "Data manipulation and analysis library for Python.", "aliases": ["Python Pandas"]},
        {"name": "NumPy", "desc": "Library for the Python programming language.", "aliases": ["Numerical Python"]},
        {"name": "Data Visualization", "desc": "Graphical representation of information and data.", "aliases": ["Data Viz", "Matplotlib", "Seaborn"]},
        {"name": "Statistics & Probability", "desc": "Mathematical concepts for data science.", "aliases": ["Statistics", "Probability", "Stats"]},
        {"name": "Data Engineering", "desc": "Designing and building systems for collecting and analyzing data.", "aliases": ["Data Pipelines", "Data Infrastructure"]},
        {"name": "Apache Spark", "desc": "Unified analytics engine for large-scale data processing.", "aliases": ["Spark", "PySpark"]},
        {"name": "ETL", "desc": "Extract, Transform, Load.", "aliases": ["ETL Pipelines", "Data Integration"]},
        {"name": "Data Warehousing", "desc": "Central repositories of integrated data.", "aliases": ["Data Warehouse", "Snowflake", "BigQuery"]},
        {"name": "Big Data", "desc": "Extremely large data sets.", "aliases": ["Big Data Analytics", "Hadoop"]},
        {"name": "Data Science", "desc": "Extracting knowledge from structured and unstructured data.", "aliases": ["Data Scientist", "Applied ML"]},
        
        # Cloud / DevOps
        {"name": "Cloud Computing", "desc": "Delivery of computing services over the internet.", "aliases": ["Cloud", "Cloud Platforms"]},
        {"name": "Amazon Web Services", "desc": "Comprehensive cloud platform provided by Amazon.", "aliases": ["AWS", "Amazon Cloud"]},
        {"name": "Microsoft Azure", "desc": "Cloud computing service by Microsoft.", "aliases": ["Azure"]},
        {"name": "Google Cloud Platform", "desc": "Suite of cloud computing services by Google.", "aliases": ["GCP", "Google Cloud"]},
        {"name": "Docker", "desc": "Platform for developing, shipping, and running applications in containers.", "aliases": ["Containerization", "Docker Containers"]},
        {"name": "Kubernetes", "desc": "Container orchestration system.", "aliases": ["K8s", "Container Orchestration"]},
        {"name": "Continuous Integration and Delivery", "desc": "Method to frequently deliver apps to customers.", "aliases": ["CI/CD", "CI CD", "Continuous Deployment"]},
        {"name": "Jenkins", "desc": "Open source automation server.", "aliases": ["Jenkins CI"]},
        {"name": "GitHub Actions", "desc": "CI/CD and automation for GitHub.", "aliases": ["GH Actions"]},
        {"name": "Infrastructure as Code", "desc": "Managing infrastructure through code.", "aliases": ["IaC", "Terraform"]},
        {"name": "Linux", "desc": "Family of open-source Unix-like operating systems.", "aliases": ["Linux OS", "Unix", "Bash"]},
        {"name": "Networking", "desc": "Computer networking fundamentals.", "aliases": ["Computer Networks", "TCP/IP"]},
        {"name": "Cloud Architecture", "desc": "Design of cloud computing systems.", "aliases": ["Cloud Design", "Cloud Solutions Architect"]},
        {"name": "Serverless", "desc": "Cloud computing execution model.", "aliases": ["Serverless Computing", "AWS Lambda"]},
        {"name": "DevOps", "desc": "Software development and IT operations.", "aliases": ["Dev Ops", "DevOps Engineering", "Site Reliability Engineering"]},
        
        # Cybersecurity
        {"name": "Cybersecurity", "desc": "Protection of computer systems and networks.", "aliases": ["InfoSec", "Information Security", "Cyber Security"]},
        {"name": "Network Security", "desc": "Policies to prevent and monitor unauthorized access.", "aliases": ["NetSec"]},
        {"name": "Application Security", "desc": "Making apps more secure.", "aliases": ["AppSec", "Secure Coding"]},
        {"name": "Ethical Hacking", "desc": "Authorized practice of bypassing system security.", "aliases": ["Penetration Testing", "Pen Testing", "White Hat Hacking"]},
        {"name": "Cryptography", "desc": "Practice of secure communication.", "aliases": ["Crypto", "Encryption"]},
        {"name": "Identity and Access Management", "desc": "Framework of policies and technologies.", "aliases": ["IAM", "Access Control"]},
        {"name": "Security Testing", "desc": "Testing software for security vulnerabilities.", "aliases": ["Vulnerability Scanning", "SecTesting"]},
        {"name": "OWASP", "desc": "Open Worldwide Application Security Project.", "aliases": ["OWASP Top 10", "Web Security"]},
        {"name": "DevSecOps", "desc": "Development, security, and operations.", "aliases": ["Secure DevOps"]},
        
        # Mobile
        {"name": "Mobile Development", "desc": "Software development for mobile devices.", "aliases": ["Mobile App Dev", "Mobile Apps"]},
        {"name": "Android Development", "desc": "Development of applications for devices running the Android operating system.", "aliases": ["Android Apps"]},
        {"name": "Kotlin", "desc": "Cross-platform, statically typed, general-purpose programming language.", "aliases": ["Kotlin Programming"]},
        {"name": "iOS Development", "desc": "Development of applications for Apple devices.", "aliases": ["iOS Apps", "iPhone App Dev"]},
        {"name": "Swift", "desc": "General-purpose, multi-paradigm, compiled programming language.", "aliases": ["Swift Programming"]},
        {"name": "Flutter", "desc": "Open-source UI software development kit.", "aliases": ["Dart", "Flutter Framework"]},
        {"name": "React Native", "desc": "Open-source UI software framework.", "aliases": ["RN"]},
        
        # Other
        {"name": "Business Intelligence", "desc": "Strategies and technologies used by enterprises for data analysis.", "aliases": ["BI", "PowerBI", "Tableau"]},
        {"name": "Product Management", "desc": "Guiding the success of a product.", "aliases": ["PM", "Product Owner"]},
        {"name": "UI/UX Design", "desc": "User interface and user experience design.", "aliases": ["UI UX", "User Experience", "User Interface"]},
        {"name": "Technical Writing", "desc": "Writing focused on providing technical information.", "aliases": ["Documentation", "Tech Writing"]},
        {"name": "Agile Methodology", "desc": "Iterative approach to software delivery.", "aliases": ["Agile", "Scrum", "Kanban"]},
        {"name": "Full Stack Developer", "desc": "Developer skilled in both frontend and backend.", "aliases": ["Fullstack", "Full-Stack Development", "Full Stack Engineering"]}
    ]
    
    new_skills_added = 0
    for data in skills_data:
        # Check if skill exists exactly by name
        existing = db.query(Skill).filter(Skill.name.ilike(data["name"])).first()
        
        if existing:
            # Update description and aliases if not set properly (idempotent enhancement)
            changed = False
            if not existing.description and data["desc"]:
                existing.description = data["desc"]
                changed = True
            if not existing.aliases and data["aliases"]:
                existing.aliases = json.dumps(data["aliases"])
                changed = True
            if changed:
                db.commit()
            continue
            
        # Also check if it exists via alias just to be safe
        skills = db.query(Skill).all()
        alias_matched = False
        for s in skills:
            if s.aliases:
                try:
                    aliases_list = json.loads(s.aliases)
                    if any(data["name"].lower() == a.lower() for a in aliases_list):
                        alias_matched = True
                        break
                except:
                    pass
        
        if not alias_matched:
            new_skill = Skill(
                name=data["name"],
                description=data["desc"],
                aliases=json.dumps(data["aliases"])
            )
            db.add(new_skill)
            new_skills_added += 1
            
    db.commit()
    final_count = db.query(Skill).count()
    print(f"Added {new_skills_added} new skills.")
    print(f"Final Skill count: {final_count}")

if __name__ == "__main__":
    seed_skills()
