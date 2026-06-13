# Master skills list — comprehensive coverage of CS/Engineering domains
MASTER_SKILLS = {
    # Programming Languages
    'Python': 'Programming', 'Java': 'Programming', 'JavaScript': 'Programming',
    'C++': 'Programming', 'C#': 'Programming', 'Go': 'Programming', 'C': 'Programming',
    'Rust': 'Programming', 'Swift': 'Programming', 'Kotlin': 'Programming',
    'PHP': 'Programming', 'Ruby': 'Programming', 'TypeScript': 'Programming',
    'Dart': 'Programming', 'R': 'Programming', 'MATLAB': 'Programming',
    'Scala': 'Programming', 'Perl': 'Programming', 'Haskell': 'Programming',
    'Objective-C': 'Programming', 'Lua': 'Programming', 'Shell Scripting': 'Programming',
    
    # Web & Mobile Frameworks
    'Django': 'Framework', 'Flask': 'Framework', 'FastAPI': 'Framework',
    'React': 'Framework', 'Angular': 'Framework', 'Vue': 'Framework',
    'NodeJS': 'Framework', 'Spring Boot': 'Framework', 'Express': 'Framework',
    'Flutter': 'Framework', 'React Native': 'Framework', 'Next.js': 'Framework',
    'Svelte': 'Framework', 'ASP.NET': 'Framework', 'Ruby on Rails': 'Framework',
    'Laravel': 'Framework', 'Bootstrap': 'Framework', 'Tailwind CSS': 'Framework',
    
    # Data & Databases
    'SQL': 'Data', 'PostgreSQL': 'Data', 'MySQL': 'Data', 'MongoDB': 'Data',
    'Redis': 'Data', 'Pandas': 'Data', 'NumPy': 'Data', 'Oracle': 'Data',
    'Cassandra': 'Data', 'Elasticsearch': 'Data', 'DynamoDB': 'Data', 'Firebase': 'Data',
    'Hadoop': 'Data', 'Spark': 'Data', 'Kafka': 'Data', 'Databricks': 'Data',
    'Power BI': 'Analytics', 'Tableau': 'Analytics', 'Snowflake': 'Data',
    
    # Cloud & DevOps
    'AWS': 'Cloud', 'Azure': 'Cloud', 'GCP': 'Cloud',
    'Docker': 'DevOps', 'Kubernetes': 'DevOps', 'Git': 'DevOps',
    'Jenkins': 'DevOps', 'Terraform': 'DevOps', 'Linux': 'DevOps',
    'Ansible': 'DevOps', 'GitHub Actions': 'DevOps', 'GitLab CI': 'DevOps',
    'Chef': 'DevOps', 'Puppet': 'DevOps', 'Bash': 'DevOps',
    
    # AI / Machine Learning / Data Science
    'Machine Learning': 'AI/ML', 'Deep Learning': 'AI/ML', 'NLP': 'AI/ML',
    'Computer Vision': 'AI/ML', 'TensorFlow': 'AI/ML', 'PyTorch': 'AI/ML',
    'Scikit-learn': 'AI/ML', 'Keras': 'AI/ML', 'Data Mining': 'AI/ML',
    'Generative AI': 'AI/ML', 'LLM': 'AI/ML', 'OpenAI': 'AI/ML',
    
    # Cybersecurity & Networks
    'Cybersecurity': 'Security', 'Penetration Testing': 'Security', 'Cryptography': 'Security',
    'Network Security': 'Security', 'Ethical Hacking': 'Security', 'SIEM': 'Security',
    'Firewalls': 'Security', 'OWASP': 'Security', 'TCP/IP': 'Networking',
    
    # Other Domains (IoT, Game Dev, Blockchain, UI/UX, etc.)
    'Blockchain': 'Other', 'Web3': 'Other', 'Smart Contracts': 'Other', 'Solidity': 'Other',
    'IoT': 'Other', 'Embedded Systems': 'Other', 'Microcontrollers': 'Other',
    'Game Development': 'Other', 'Unity': 'Other', 'Unreal Engine': 'Other',
    'UI/UX Design': 'Other', 'Figma': 'Other', 'REST API': 'Other', 'GraphQL': 'Other', 
    'Microservices': 'Other', 'Agile': 'Other', 'Scrum': 'Other', 'JIRA': 'Other',
}

class SkillExtractor:
    SKILL_ALIASES = {
        # AI/ML & Data Science
        'ml': 'Machine Learning', 'artificial intelligence': 'Machine Learning', 'ai': 'Machine Learning',
        'dl': 'Deep Learning', 'nlp': 'NLP', 'natural language processing': 'NLP',
        'cv': 'Computer Vision', 'llms': 'LLM', 'large language models': 'LLM',
        'gen ai': 'Generative AI', 'genai': 'Generative AI', 'tf': 'TensorFlow',
        
        # Web & Frameworks
        'js': 'JavaScript', 'ts': 'TypeScript', 'node.js': 'NodeJS', 'node': 'NodeJS', 'nodejs': 'NodeJS',
        'reactjs': 'React', 'react.js': 'React', 'vuejs': 'Vue', 'vue.js': 'Vue',
        'angularjs': 'Angular', 'angular.js': 'Angular', 'nextjs': 'Next.js', 'next js': 'Next.js',
        'rn': 'React Native', 'spring': 'Spring Boot', 'springboot': 'Spring Boot',
        'rails': 'Ruby on Rails', 'ror': 'Ruby on Rails', '.net': 'ASP.NET', 'dot net': 'ASP.NET',
        
        # Languages
        'c/c++': 'C++', 'cpp': 'C++', 'cxx': 'C++', 'csharp': 'C#', 'c#': 'C#',
        'golang': 'Go', 'py': 'Python', 'obj-c': 'Objective-C', 'objective c': 'Objective-C',
        'sh': 'Shell Scripting', 'shell': 'Shell Scripting',
        
        # Data & Databases
        'postgres': 'PostgreSQL', 'psql': 'PostgreSQL', 'sql server': 'SQL Server', 'mssql': 'SQL Server',
        'mongo': 'MongoDB', 'elastic search': 'Elasticsearch', 'elastic': 'Elasticsearch',
        
        # Cloud & DevOps
        'k8s': 'Kubernetes', 'kube': 'Kubernetes', 'aws': 'AWS', 'amazon web services': 'AWS',
        'gcp': 'GCP', 'google cloud platform': 'GCP', 'google cloud': 'GCP', 
        'azure': 'Azure', 'microsoft azure': 'Azure', 'ci/cd': 'DevOps',
        
        # Security & Networks
        'infosec': 'Cybersecurity', 'pentesting': 'Penetration Testing', 'pen testing': 'Penetration Testing',
        'crypto': 'Cryptography', 'ethical hacker': 'Ethical Hacking',
        
        # Other Domains
        'ui': 'UI/UX Design', 'ux': 'UI/UX Design', 'ui/ux': 'UI/UX Design',
        'dlt': 'Blockchain', 'crypto currency': 'Blockchain', 'smart contract': 'Smart Contracts',
        'vr': 'AR/VR', 'ar': 'AR/VR', 'virtual reality': 'AR/VR', 'augmented reality': 'AR/VR',
    }

    def extract(self, text: str) -> list:
        """
        Regex boundary-based extraction. Returns list of {'skill_name', 'category'} dicts.
        """
        import re
        text_lower = text.lower()
        found = {}
        
        # 1. Search for primary master skills using boundaries
        for skill, category in MASTER_SKILLS.items():
            pattern = r'\b' + re.escape(skill.lower()) + r'\b'
            if re.search(pattern, text_lower):
                found[skill] = category
                
        # 2. Search for aliases
        for alias, actual_skill in self.SKILL_ALIASES.items():
            # If the actual skill isn't already found
            if actual_skill not in found:
                pattern = r'\b' + re.escape(alias.lower()) + r'\b'
                if re.search(pattern, text_lower):
                    category = MASTER_SKILLS.get(actual_skill, 'Other')
                    found[actual_skill] = category
                    
        return [{'skill_name': k, 'category': v} for k, v in found.items()]

class EducationExtractor:
    def extract(self, text: str) -> str:
        """Returns a standardized string representing the highest education level."""
        text_lower = text.lower()
        
        # Check from highest to lowest degree
        if any(kw in text_lower for kw in ['phd', 'doctorate']):
            return 'PhD / Doctorate'
        elif any(kw in text_lower for kw in ['master', 'm.sc', 'm.e', 'm.tech', 'mba']):
            return 'Masters Degree'
        elif any(kw in text_lower for kw in ['bachelor', 'b.sc', 'b.e', 'b.tech']):
            return 'Bachelors Degree'
        elif any(kw in text_lower for kw in ['diploma', 'associate']):
            return 'Diploma / Associate'
            
        return "Not specified"

class ExperienceExtractor:
    def extract(self, text: str) -> float:
        """Extract years of experience as float."""
        import re
        patterns = [
            r'(\d+(?:\.\d+)?)\s*(?:\+\s*)?years?\s+(?:of\s+)?experience',
            r'experience\s+of\s+(\d+(?:\.\d+)?)\s*years?',
            r'(\d+(?:\.\d+)?)\s*yrs?\s+(?:of\s+)?exp',
        ]
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                return float(match.group(1))
        return 0.0

class CertificationExtractor:
    CERT_KEYWORDS = [
        'certified', 'certificate', 'certification', 'aws certified',
        'pmp', 'cissp', 'ccna', 'google certified', 'azure certified',
        'oracle certified', 'comptia', 'itil',
    ]
    def extract(self, text: str) -> list:
        """Returns list of certification strings found in text."""
        import re
        found = []
        sentences = re.split(r'[.\n]', text)
        for sentence in sentences:
            if any(kw in sentence.lower() for kw in self.CERT_KEYWORDS):
                cert = sentence.strip()
                if 5 < len(cert) < 200:
                    found.append(cert)
        return found[:5]   # cap at 5

class EmailExtractor:
    def extract(self, text: str) -> str:
        import re
        match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
        return match.group(0) if match else ""

class PhoneExtractor:
    def extract(self, text: str) -> str:
        import re
        match = re.search(r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text)
        return match.group(0) if match else ""

class NameExtractor:
    def extract(self, text: str) -> str:
        import re
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        if lines:
            line = lines[0]
            # Clean up if it grabbed "Resume" or "Curriculum Vitae"
            if line.lower() in ['resume', 'curriculum vitae', 'cv'] and len(lines) > 1:
                line = lines[1]
                
            # Strip out emails
            line = re.sub(r'[\w\.-]+@[\w\.-]+\.\w+', '', line)
            # Strip out phone numbers
            line = re.sub(r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', '', line)
            # Strip out urls (linkedin, etc)
            line = re.sub(r'http[s]?://\S+', '', line)
            line = re.sub(r'www\.\S+', '', line)
            # Remove any lingering special characters or numbers, leave only letters and spaces
            line = re.sub(r'[^A-Za-z\s]', ' ', line)
            
            # Collapse multiple spaces
            name = re.sub(r'\s+', ' ', line).strip()
            
            # Cap at 50 chars and title case
            return name[:50].title() if name else "Unknown Candidate"
        return "Unknown Candidate"
