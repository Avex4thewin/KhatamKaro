from app import app
from models import db, Subject, Chapter

SUBJECT_DATA = {

    "Mathematics": {
        "XI": [
            "Sets",
            "Relations and Functions",
            "Trigonometric Functions",
            "Principle of Mathematical Induction",
            "Complex Numbers",
            "Quadratic Equations",
            "Linear Inequalities",
            "Permutations and Combinations",
            "Binomial Theorem",
            "Sequence and Series",
            "Straight Lines",
            "Circles",
            "Conic Sections",
            "Introduction to Three-Dimensional Geometry",
            "Limits and Derivatives",
            "Mathematical Reasoning",
            "Statistics",
            "Probability",
            "Correlation Analysis",
            "Index Numbers and Moving Averages",
        ],
        "XII": [
            "Relations and Functions",
            "Inverse Trigonometric Functions",
            "Matrices",
            "Determinants",
            "Continuity and Differentiability",
            "Application of Derivatives",
            "Integrals",
            "Applications of Integrals",
            "Differential Equations",
            "Vector Algebra",
            "Three Dimensional Geometry",
            "Linear Programming",
            "Probability",
            "Linear Regression",
        ],
    },


    "Applied Mathematics": {
        "XI": [
            "Numbers, Quantification and Numerical Applications",
            "Algebra",
            "Mathematical Reasoning",
            "Calculus",
            "Probability",
            "Descriptive Statistics",
            "Basics of Financial Mathematics",
            "Coordinate Geometry",
            "Sequence and Series",
            "Permutations and Combinations",
            "Introduction to Three Dimensional Geometry",
            "Inferential Statistics",
        ],
        "XII": [
            "Numbers, Quantification and Numerical Applications",
            "Algebra",
            "Mathematical Reasoning",
            "Calculus",
            "Probability",
            "Descriptive Statistics",
            "Financial Mathematics",
            "Coordinate Geometry",
            "Linear Programming",
            "Inferential Statistics",
            "Index Numbers and Time Based Data",
        ],
    },


    "English Language": {
        "XI": [
            "Composition",
            "Directed Writing",
            "Proposal Writing",
            "Comprehension",
            "Grammar",
        ],
        "XII": [
            "Composition",
            "Directed Writing",
            "Proposal Writing",
            "Comprehension",
            "Grammar",
        ],
    },


    "Literature in English": {
        "XI": [
            "Macbeth",
            "Prism - A Living God",
            "Prism - Advice to Youth",
            "Prism - The Paper Menagerie",
            "Prism - The Great Automatic Grammatizator",
            "Prism - Thank You, Ma'am",
            "Rhapsody - Abhisara: The Tryst",
            "Rhapsody - Why I Like the Hospital",
            "Rhapsody - Sonnet 116",
            "Rhapsody - Death of a Naturalist",
            "Rhapsody - Strange Meeting",
        ],
        "XII": [
            "Macbeth",
            "Prism - Atithi / Guest",
            "Prism - The Cookie Lady",
            "Prism - There Will Come Soft Rains",
            "Prism - Indigo",
            "Prism - The Medicine Bag",
            "Rhapsody - Telephone Conversation",
            "Rhapsody - Tithonus",
            "Rhapsody - Beethoven",
            "Rhapsody - Small Towns and the River",
            "Rhapsody - Death be not Proud",
        ],
    },


    "Physics": {
        "XI": [
            "Physical World and Measurement",
            "Kinematics",
            "Laws of Motion",
            "Work, Energy and Power",
            "Motion of a System of Particles and a Rigid Body",
            "Gravitation",
            "Properties of Bulk Matter",
            "Heat and Thermodynamics",
            "Behaviour of Perfect Gases and Kinetic Theory of Gases",
            "Oscillations and Waves",
        ],
        "XII": [
            "Electrostatics",
            "Current Electricity",
            "Magnetic Effects of Current and Magnetism",
            "Electromagnetic Induction and Alternating Currents",
            "Electromagnetic Waves",
            "Optics",
            "Dual Nature of Radiation and Matter",
            "Atoms and Nuclei",
            "Electronic Devices",
        ],
    },


    "Chemistry": {
        "XI": [
            "Some Basic Concepts of Chemistry",
            "Structure of Atom",
            "Classification of Elements and Periodicity in Properties",
            "Chemical Bonding and Molecular Structure",
            "States of Matter",
            "Chemical Thermodynamics",
            "Equilibrium",
            "Redox Reactions",
            "Organic Chemistry: Some Basic Principles and Techniques",
            "Hydrocarbons",
            "Environmental Chemistry",
        ],
        "XII": [
            "Solutions",
            "Electrochemistry",
            "Chemical Kinetics",
            "d- and f-Block Elements",
            "Coordination Compounds",
            "Haloalkanes and Haloarenes",
            "Alcohols, Phenols and Ethers",
            "Aldehydes, Ketones and Carboxylic Acids",
            "Organic Compounds Containing Nitrogen",
            "Biomolecules",
        ],
    },


    "Computer Science": {
        "XI": [
            "Introduction to Object Oriented Programming",
            "Java as an Object Oriented Programming Language",
            "Elementary Data Representation",
            "Operators in Java",
            "Basic Programming Concepts",
            "Conditional Statements",
            "Iterative Statements",
            "Nested Loops",
            "Methods",
            "Arrays",
            "String Handling",
            "Classes and Objects",
        ],
        "XII": [
            "Boolean Algebra",
            "Computer Hardware",
            "Data Structures",
            "Recursion",
            "Complexity of Algorithms",
            "Data Representation",
            "Computer Networks",
            "Database Concepts",
            "Java Programming",
        ],
    },


    "Biology": {
        "XI": [
            "Diversity of Living Organisms",
            "Structural Organisation in Animals and Plants",
            "Cell: Structure and Function",
            "Plant Physiology",
            "Human Physiology",
        ],
        "XII": [
            "Reproduction",
            "Genetics and Evolution",
            "Biology and Human Welfare",
            "Biotechnology and its Applications",
            "Ecology and Environment",
        ],
    },


    "Physical Education": {
        "XI": [
            "Concept of Physical Education",
            "Physical Fitness and Wellness",
            "Sports and Games",
            "Yoga",
            "Physical Education and Sports for CWSN",
            "First Aid and Safety Education",
            "Nutrition",
            "Psychology and Sports",
            "Training Methods",
        ],
        "XII": [
            "Socio-Cultural Factors in Sports and Games",
            "Effects of Exercise on Muscular and Circulatory Systems",
            "Career Aspects in Physical Education",
            "Physical Education and Sports for CWSN",
            "Individual Sports",
            "Team Sports",
            "Yoga",
            "Doping",
            "Sports Medicine",
            "Nutrition and Sports",
        ],
    },


    "Commerce": {
        "XI": [
            "Nature and Purpose of Business",
            "Forms of Business Organisation",
            "Social Responsibility of Business and Business Ethics",
            "Emerging Modes of Business",
            "Stock Exchange",
            "Trade",
            "Foreign Trade",
            "Insurance",
        ],
        "XII": [
            "Business Environment",
            "Entrepreneurship",
            "Business Management",
            "Marketing",
            "Human Resource Management",
            "Financial Management",
            "Business Communication",
            "Consumer Protection",
        ],
    },


    "Economics": {
        "XI": [
            "Understanding Economics",
            "Indian Economic Development",
            "Statistics",
        ],
        "XII": [
            "Microeconomic Theory",
            "Theory of Income and Employment",
            "Money and Banking",
            "Balance of Payments and Foreign Exchange Rate",
            "Public Finance",
            "National Income",
            "Economic Growth and Development",
            "Indian Economy",
        ],
    },


    "Business Studies": {
        "XI": [
            "Business Environment",
            "Entrepreneurship",
            "Forms of Business Organisation",
            "Joint Stock Company",
            "Public Sector",
            "Globalisation and Business",
            "Internal Trade",
            "Emerging Modes of Business",
        ],
        "XII": [
            "Nature and Significance of Management",
            "Principles of Management",
            "Business Environment",
            "Planning",
            "Organising",
            "Staffing",
            "Directing",
            "Controlling",
            "Financial Management",
            "Marketing Management",
            "Consumer Protection",
            "Entrepreneurship",
        ],
    },


    "Entrepreneurship": {
        "XI": [
            "Introduction to Entrepreneur",
            "Introduction to Entrepreneurship",
            "Intrapreneurship",
            "Enterprise",
            "Business Planning",
            "Enterprise Marketing",
            "Resource Mobilisation",
        ],
        "XII": [
            "Entrepreneurship",
            "Business Ideation",
            "Enterprise Planning",
            "Enterprise Marketing",
            "Resource Mobilisation",
            "Enterprise Growth Strategies",
        ],
    },


    "Psychology": {
        "XI": [
            "Introduction to Psychology",
            "Methods of Psychology",
            "Human Development",
            "Sensory, Attentional and Perceptual Processes",
            "Learning",
            "Human Memory",
            "Thinking",
            "Motivation and Emotion",
        ],
        "XII": [
            "Intelligence and Ability",
            "Personality",
            "Lifespan Development",
            "Stress and Stress Management",
            "Psychological Disorders",
            "Therapeutic Approaches",
            "Social Cognition",
            "Attitude and Social Cognition",
            "Social Influence and Group Processes",
            "Psychology and Education",
            "Psychology and Health",
        ],
    },


    "Hindi": {
        "XI": [
            "Saara Aakash",
            "Aashad Ka Ek Din",

            "Gadya Sankalan - Putra Prem",
            "Gadya Sankalan - Gauri",
            "Gadya Sankalan - Sharanagat",
            "Gadya Sankalan - Sati",
            "Gadya Sankalan - Outsider",
            "Gadya Sankalan - Dasi",
            "Gadya Sankalan - Kya Nirash Hua Jaye",
            "Gadya Sankalan - Bhaktin",
            "Gadya Sankalan - Sanskriti Kya Hai",
            "Gadya Sankalan - Majburi",

            "Kavya Manjari - Sakhi",
            "Kavya Manjari - Balleela",
            "Kavya Manjari - Ek Phool Ki Chah",
            "Kavya Manjari - Aah Dharati Kitna Deti Hai",
            "Kavya Manjari - Nadi Ke Dweep",
            "Kavya Manjari - Tulsi Das Ke Pad",
            "Kavya Manjari - Jag Tujhko Door Jana Hai",
            "Kavya Manjari - Udyami Nar",
            "Kavya Manjari - Badal Ko Ghirte Dekha Hai",
            "Kavya Manjari - Andhere Ka Deepak",
        ],

        "XII": [
            "Saara Aakash",
            "Aashad Ka Ek Din",

            "Gadya Sankalan - Putra Prem",
            "Gadya Sankalan - Gauri",
            "Gadya Sankalan - Sharanagat",
            "Gadya Sankalan - Sati",
            "Gadya Sankalan - Outsider",
            "Gadya Sankalan - Dasi",
            "Gadya Sankalan - Kya Nirash Hua Jaye",
            "Gadya Sankalan - Bhaktin",
            "Gadya Sankalan - Sanskriti Kya Hai",
            "Gadya Sankalan - Majburi",

            "Kavya Manjari - Sakhi",
            "Kavya Manjari - Balleela",
            "Kavya Manjari - Ek Phool Ki Chah",
            "Kavya Manjari - Aah Dharati Kitna Deti Hai",
            "Kavya Manjari - Nadi Ke Dweep",
            "Kavya Manjari - Tulsi Das Ke Pad",
            "Kavya Manjari - Jag Tujhko Door Jana Hai",
            "Kavya Manjari - Udyami Nar",
            "Kavya Manjari - Badal Ko Ghirte Dekha Hai",
            "Kavya Manjari - Andhere Ka Deepak",
        ],
    },


    "Bengali": {
        "XI": [
            "কণী - অধ্যায় ১-৮",
            "মুকুট - অঙ্ক ১ ও ২",
            "ঠাকুরদা",
            "জোড়াসাঁকোর ধারে",
            "তাসের ঘর",
            "অনাচার",
            "রেকর্ড",
            "ওরা কাজ করে",
            "পূব-পশ্চিম",
            "বনলতা সেন",
            "বর্ণপরিচয়",
            "সালেমনের মা",
        ],
        "XII": [
            "কণী - অধ্যায় ৯-১৪",
            "মুকুট - অঙ্ক ৩",
            "বীর্যশুল্ক",
            "আদাব",
            "লছমনের মা",
            "একটি তুলসী গাছের কাহিনী",
            "না পাহাড়ার পরীক্ষা",
            "বাবরের প্রার্থনা",
            "যদি নির্বাসন দাও",
            "রাস্তা কারোর একার নয়",
            "স্বাধীনতা তুমি",
            "নুন",
        ],
    },


    "Environmental Studies/Science": {
        "XI": [
            "Modes of Existence",
            "Ecology",
            "Population",
            "Environmental Pollution",
            "Energy",
            "Natural Resources",
            "Environmental Management",
        ],
        "XII": [
            "Population",
            "Water Resources",
            "Land Resources",
            "Energy Resources",
            "Biodiversity",
            "Environmental Pollution",
            "Environmental Management",
            "Global Environmental Issues",
        ],
    },


    "History": {
        "XI": [
            "Emergence of the Colonial Economy",
            "Social Movements",
            "Protest Movements against Colonial Rule",
            "Gandhian Nationalism",
            "Growth of Nationalism",
            "Constitutional Developments",
            "The United Nations",
            "The Cold War",
        ],
        "XII": [
            "Emergence of the Colonial Economy",
            "Social Movements",
            "Protest Movements against Colonial Rule",
            "Growth of Nationalism",
            "Gandhian Nationalism (1916-1922)",
            "Gandhian Nationalism (1922-1939)",
            "The Beginning of the End of the British Raj",
            "Towards Independence and Partition",
            "The World after World War II",
        ],
    },


    "Geography": {
        "XI": [
            "Geography as a Discipline",
            "Formation of the Earth",
            "Changing Face of the Earth",
            "Atmosphere",
            "The Realms of Water",
            "Biosphere - Life on the Earth",
            "Map Work",
        ],
        "XII": [
            "Physical Environment",
            "Population",
            "Human Settlements",
            "Resources",
            "Agriculture",
            "Water Resources",
            "Mineral and Energy Resources",
            "Manufacturing Industries",
            "Transport and Communication",
            "International Trade",
            "Map Work",
        ],
    },


    "Art": {
        "XI": [
            "Still Life",
            "Drawing or Painting from Nature",
            "Drawing or Painting of a Living Person",
            "Imaginative Composition",
            "Craft",
            "Craftwork",
        ],
        "XII": [
            "Still Life",
            "Drawing or Painting from Nature",
            "Drawing or Painting of a Living Person",
            "Imaginative Composition",
            "Craft",
            "Craftwork",
        ],
    },


    "Sociology": {
        "XI": [
            "Individual and Society",
            "Socialization",
            "Culture",
            "Origin and Development of Sociology and Anthropology",
            "Research Methodology",
            "Indian Sociologists",
            "Social Structure",
            "Social Problems",
        ],
        "XII": [
            "Social Institutions",
            "Religion and Society",
            "Political Organisation",
            "Economic Organisation",
            "Social Stratification",
            "Social Change",
            "Social Movements",
            "Mass Media and Society",
            "Globalisation and Society",
        ],
    },

}


CLASS_MAP = {"XI": 11, "XII": 12}

def seed():
    with app.app_context():
        for subject_name, classes in SUBJECT_DATA.items():
            subject = Subject.query.filter_by(name=subject_name).first()
            if not subject:
                subject = Subject(name=subject_name)
                db.session.add(subject)
                db.session.commit()
                print(f"Created subject: {subject_name}")

            for class_str, chapters in classes.items():
                class_level = CLASS_MAP.get(class_str)
                for chapter_name in chapters:
                    existing = Chapter.query.filter_by(
                        name=chapter_name, subject_id=subject.id, class_level=class_level
                    ).first()
                    if not existing:
                        chapter = Chapter(name=chapter_name, subject_id=subject.id, class_level=class_level)
                        db.session.add(chapter)
                        print(f"  [{class_str}] {chapter_name}")

        db.session.commit()
        print("Seeding complete.")

if __name__ == '__main__':
    seed()