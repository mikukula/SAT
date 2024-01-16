class DefaultRoles:
    def __init__(self):
        self.roles = ["CEO", "CFO", "CPO", "CISO", "CIO", "CTO"]
        self.descriptions = ["A CEO, or Chief Executive Officer, is the top executive in an organization responsible for making major corporate decisions, managing overall operations, and implementing strategies to ensure the company's success.",
                             "A CFO, or Chief Financial Officer, is a key executive responsible for managing an organization's financial aspects.",
                             "A CPO, or Chief Product Officer, is a senior executive responsible for overseeing the development and management of a company's product strategy.",
                             "A CISO, or Chief Information Security Officer, is a senior executive responsible for the overall cybersecurity strategy and management within an organization.",
                             "A CIO, or Chief Information Officer, is a senior executive responsible for overseeing the management and strategic use of information technology (IT) within an organization.",
                             "A CTO, or Chief Technology Officer, is a senior executive responsible for the technological direction and innovation within an organization."]

class DefaultQuestions:
    def __init__(self):
        self.question_text = ["Which of the following technologies are utilised within your organisation (i.e. they are in use somewhere to some extent)?",
                              "How would you rate your organisation’s overall dependence upon IT devices?",
                              "Which of the following technologies do you believe are critical within your organisation (i.e. day-to-day operations depend upon them)?",
                              "Which of the following types of data is stored and processed on your organisation’s devices?",
                              "How would you rate your overall resilience to technology-based disruption?",
                              "Devices currently deployed in the organisation are protected from security vulnerabilities and breaches?",
                              ]
        
        self.category = []
class DefaultCategories:
    def __init__(self):
        self.categoryID = ["TDU", "IAB", "SPI", "STA", "DSA"]

        self.name = ["Technology and data usage", "Incidents and breaches", "Security priority and investment",
                     "Security in technology adoption", "DSbD-specific awareness"]
        
        self.rationale = ["The need for security based upon what the organisation is using the technology for, its dependence upon it, etc.",
                          "Highlights the organisation’s need for security based upon evidence of exposure, plus suggests the extent to which it already on the agenda.",
                          "Attitudes toward security in the organisation as a whole.",
                          "More specific focus upon considerations at the technology investment level (i.e. which is more likely to affect DSbD adoption decisions).",
                          "More specifically focused on the CISO/CTO elements of the organisation to determine how well positioned they are to keep up to date with what is available to be adopted. Can also be used to raise awareness of DSbD."]
        
        self.rating = ['need', 'need', 'attitude', 'attitude', 'awareness']