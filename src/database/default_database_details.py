class DefaultRoles:
    def __init__(self):
        self.roles = ["UNIVERSAL", "CEO", "CFO", "CPO", "CISO", "CIO", "CTO"]
        self.descriptions = ["No role is assigned. This role should only be assigned to administrators who are not supposed to take part in surveys and only manage the system.",
                             "A CEO, or Chief Executive Officer, is the top executive in an organization responsible for making major corporate decisions, managing overall operations, and implementing strategies to ensure the company's success.",
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
                                "Direct prior experiences of security incidents or breaches have increased your organisation’s need for cybersecurity measures.",
                                  "Reporting of incidents and breaches within other organisations has increased your own attention towards cybersecurity.",
                                  "Which of the following do you believe that your organisation has experienced in the last 12 months?",
                                  "Which of the following are you most concerned about?",
                                  "Has your organisation experienced any incidents that you would link directly to the exploitation of hardware-based vulnerabilities?",
                                  "Has your organisation experienced any incidents that you would link directly to the exploitation of software-based vulnerabilities?",
                                  "The organisation would be interested in implementing more secure technologies that would reduce exploitation-based security breaches.",
                                  "To what extent are you aware of any instances of own products being compromised?",
                                  "What effect has awareness of incidents and breaches had upon your organisation’s priority towards cybersecurity in budgeting and financial planning?",
                                  "The organisation has invested more in cybersecurity as a direct response to prior incidents or breaches.",
                                  "Security is a high priority for our organisation",
                                  "Security receives sufficient attention and resourcing in the organisation",
                                  "Approximately what proportion of your organisations IT budget do you estimate is allocated to cyber security?",
                                  "Security receives a sufficient level of upper management support.",
                                  "What factors drive your security investments?",
                                  "What challenges does your organisation face in driving security investments?",
                                  "Other parts of the organisation recognise and prioritise security to the same extent as you?",
                                  "The organisation would review its security investments in response to changes in available controls and safeguards?",
                                  "The organisation would review its security investments in response to changes in the threat landscape?",
                                  "To what extent would you be willing to invest in new/additional technology adoption to improve cyber security?",
                                    "What factors should influence the adoption of any new security technologies?",
                                  "When purchasing new technology for general use, how much more would the organisation be prepared to spend for a ‘more secure’ device?",
                                  "When purchasing new technology for critical systems, how much more would the organisation be prepared to spend for a 'more secure' device",
                                  "Which of the following factors is the most important in the context of your technology investments?",
                                  "When considering technology device purchases, how would you rate your organisation’s priority?",
                                  "How important are manufacturer/vendor security assurances when procuring new devices?",
                                  "Manufacturer/vendor security assurances are evaluated when procuring new devices?",
                                  "How would you rate the resilience of your current devices against hardware vulnerabilities?",
                                  "Improving security justifies additional effort/cost to integrate it within our products?",
                                  "Do you promote security as a relevant feature of your own product(s)?",
                                  "Do you believe that the security aspects of your product(s) are important to customers?",
                                  "How familiar are you with the concept of Digital Security by Design (DSbD), which promoted secure-by-design principles in technology development?",
                                   "Your organisation would select a secure by design technology if it marginally (e.g. <10%) increased the unit cost per device.",
                                   "Your organisation would select a secure by design technology if it significantly (e.g. >10%) increased the unit cost per device.",
                                   "Your organisation would select a secure by design technology if it would reduce security vulnerabilities.",
                                   "What are the key factors that your organization would need to consider if adopting a Digital Security by Design technology solution?",
                                   "What obstacles would you face if migrating from your current technology to secure by design devices?",
                                   "Are you aware of the National Cyber Security Centre’s Secure by Default principles?",
                                   "If Yes to above Do you follow them in the development of your own product(s)?",
                                   "If No to Q8 or Partially to Q9 What would your organisation need in order to better support the development of products that are secure by design?"]
        
        self.rationale = ["Aims to get a sense of the level and extent of technology usage.",
                          "To assess the organisation’s sense of how much they depend upon technology devices.",
                          "Aiming to explore the dependency issue more fully by linking to particular types of technology.",
                          "The nature of the data used informs the resulting need for protection.",
                          "Aiming to get a broad sense of how well protected the organisation considers itself to be.",
                          "A more specific insight into the issue of protection and resilience.",
                          "Prior experience of incidents already demonstrates a need for security.",
                          "Experiences within other organisations provides evidence of issues, even if not experienced at first hand.",
                          "Enables a sense of the range of incidents that have been experienced. The list is intended to be indicative rather than exhaustive, and several incident types are unrelated to the areas where DSbD would help. The idea would be to get a sense of the breach experiences overall relative to those where DSbD could be a factor.",
                          "Will offer a basis for assessing whether concerns are aligned with experiences.",
                          "Assessing experience of vulnerabilities that may be more directly addressed by the adoption of DSbD-based approaches.",
                          "Assessing experience of vulnerabilities that may be avoided by the adoption of DSbD-based approaches.",
                          "In cases where the organisation produces its own technology products, have these fallen victim to security issues and (if so) the extent to which users have been affected.",
                          "Assessing whether awareness of incidents or breaches has been a factor in changing the level of priority / attention given to cybersecurity in related financial resourcing.",
                          "Determining whether direct experience of incidents or breaches by the organisation has led to resulting investment.",
                          "To provide a sense of the overall view about security from different perspectives.",
                          "Separately from how it was rated in terms of the perceived priority, this considers whether the attention given is sufficient.",
                          "A more specific insight into the level of financial resource directed towards cyber security.",
                          "Interesting to see if upper management’s own views align with other parts of the business.",
                          "Security investment can be motivated by a number of push and pull factors, which may be perceived differently by different stakeholders within the organisation.",
                          "Various practical and operational challenges may exist, which may be perceived differently by different stakeholders within the organisation.",
                          "This aims to get a sense of whether members of the organisation feel their priorities are collectively aligned.",
                          "This helps to assess the extent to which the organisations’ approach to cyber security is driven by opportunities to improve protection.",
                          "This helps to assess the extent to which the organisations’ approach to cyber security is driven by perceived threats.",
                          "This links the willingness to adopt additional cyber security measures to the cost of doing so.",
                          "Aims to establish what factors are likely to be considered when new technologies are specifically adopted to support security.",
                          "Assesses the organisation’s appetite for security investment in terms of general IT use.",
                          "Assesses the organisation’s appetite for security investment in terms of protecting systems specifically recognised as being the most important.",
                          "Security, cost and usability are often factors that play against each other, it is relevant to know how they are viewed by different stakeholders.",
                          "Specifically comparing security against the cost of achieving it.",
                          "To gauge the extent to which security assurances are being considered and valued when the organisation invests its IT devices.",
                          "Beyond an assurance being present, are efforts made to see what it means and whether it is relevant?",
                          "Aims to assess whether there are already any recognised issues from the device security perspective and/or attention directed in this area.",
                          "Is the organisation willing to accept additional overheads to produce more security products?",
                          "Is security considered to be an important factor in the organisation’s own product marketing?",
                          "Is product security something that customers are likely to be looking for or attracted by?",
                          "DSbD is the basis upon which future products may be better secured, and so it is relevant to determine which stakeholders may be aware of it.",
                          "Aiming to establish the additional cost threshold at which DSbD adoption would be an acceptable proposition.",
                          "Aiming to establish the additional cost threshold at which DSbD adoption would be an acceptable proposition, now at a higher threshold.",
                          "Assessing the extent to the threshold at which improvements in security would motivate the adoption of improved technology.",
                          "DSbD adoption is likely to need to be considered in the context of a range of practical and operation factors.",
                          "Changing from one technology to another may be challenged by a range of practical and operational factors.",
                          "The Secure by Design principles are intended to help inform the appropriate consideration and provision of security in new products, and so relevant to an organisation developing its own products.",
                          "Assesses if any declared knowledge is put into practice.",
                          "In cases where the NCSC principles are not known or only partially followed, it is relevant to determine if any obstacles to full compliance are recognised."]

        self.comments = ["The focus is now more specifically placed upon IT devices, as this is the level at which where CHERI / Morello would ultimately feature.",
                         "There could be options for deeper investigation here, e.g. - to rate the proportion of data they hold within each category - to indicate which types of data sit on which types of device. Both aspects would significantly extend the length of the TDU section.",
                         "Only requested from the stakeholders with more technical knowledge of the situation.",
                         "CPO not expected to know this information, but other stakeholders should have a sense of it.",
                         "More specific detail for which only the technical stakeholders would have relevant insights.",
                         "Again, an area where only the technical stakeholders would have insight.",
                         "Asking this here provides a basis for comparing to responses in SPI and STA sections.",
                         "A potential opportunity for DSbD to contribute to improving the products offered. CEO and technical stakeholders expected to be the ones with awareness here.",
                         "The CPO is omitted as they are unlikely to be the decision maker or influencer here, because although they handle procurement, they are not expected to have the background knowledge of incidents and breaches.",
                         "In all cases it is interesting to get a sense of how the issues look from different stakeholder perspectives.",
                         "Same list of options as DSA Q7.",
                         "This can be used as a comparison to responses from the STA section.",
                         "Provides a basis for comparison with the response to Q5 from the SPI section (i.e. this question asks what should influence adoption, whereas the other asked what their drivers are).",
                         "DSbD-based devices would likely be marketed as being more secure on the basis of being secure by design, and so what would this count for with the stakeholders.",
                         "Probably not an issue on which the CPO has a specific view.",
                         "While non-technical stakeholders would not be expected to be familiar, it would be relevant to gauge name-recognition (esp. for firms producing their own products).",
                         "Can be set against the responses to STA Q2 and Q3.",
                         "Can link to responses from the STA section.",
                         "The responses here may be useful as a comparison against earlier questions about investment drivers and challenges.",
                         "Same list of options as SPI Q6.",
                         "In a company that develops its own products, this seems like a reasonable thing to ask the CEO, as they could be expected to know.",
                         "This would need the question database to have a field for to show that a question is conditional on the response to a prior question."]
class DefaultCategories:
    def __init__(self):
        self.categoryID = ["TDU", "IAB", "SPI", "STA", "DSA"]

        self.name = ["Technology and Data Usage", "Incidents and Breaches", "Security Priority and Investment",
                     "Security in Technology Adoption", "DSbD-specific Awareness"]
        
        self.rationale = ["The need for security based upon what the organisation is using the technology for, its dependence upon it, etc.",
                          "Highlights the organisation’s need for security based upon evidence of exposure, plus suggests the extent to which it already on the agenda.",
                          "Attitudes toward security in the organisation as a whole.",
                          "More specific focus upon considerations at the technology investment level (i.e. which is more likely to affect DSbD adoption decisions).",
                          "More specifically focused on the CISO/CTO elements of the organisation to determine how well positioned they are to keep up to date with what is available to be adopted. Can also be used to raise awareness of DSbD."]
        
        self.rating = ['need', 'need', 'attitude', 'attitude', 'awareness']

class DefaultAnswers:
    def __init__(self):
        
        self.answer_text = [
                            "Strongly Agree;Agree;Neutral;Disagree;Strongly Disagree",
                            "Strongly Agree;Agree;Neutral;Disagree;Strongly Disagree;N/D",
                            "Desktop / laptop PCs;Smartphones and tablets;Consumer grade smart devices;Enterprise IoT / IIoT devices;Cloud-based storage;Cloud-based applications / services;Operational Technology (OT);Embedded technologies;Unable to judge",
                            "Highly dependent;Somewhat dependent (we could briefly operate without it);We use it, but could manage without it;Not at all dependent;Dpn't know",
                            "Client/Customer sensitive;Commercially sensitive;National security;Personally identifiable information;Proprietary Intellectual Property;Don’t know;Other",
                            "Strongly resilient;Somewhat resilient;Not very resilient;Not at all resilient;Don’t know",
                            "Data loss or exposure;Denial of Service attacks;Device loss or theft;Hacking;Insider attacks/misuse;Malware (e.g. ransomware, spyware, virus);Phishing;Physical breach;System or device failure;User error leading to a security breach;Other",
                            "No;Rarely;Occasionally;Frequently;Don’t Know",
                            "Not aware of any issues;Aware of unexploited vulnerabilities;Isolated incident(s);Moderate issue affecting some users;Large scale issue affecting many users",
                            "Significantly lower priority;Somewhat lower priority;Unchanged priority;Somewhat higher priority;Significantly higher priority",
                            "Less than 1%;1-5%;6-10%;11-20%;Over 20%",
                            "Protection against known cyber threats;Previous security incidents or breaches;Compliance with regulations and standards;Safeguarding data and information;Business continuity;Customer satisfaction;Protecting brand/company/organization reputation;Other",
                            "None;Don’t know;Limited budget/resources;Lack of awareness/understanding of security risks;Difficulty in prioritizing security investments against other competing priorities;Lack of executive support and commitment;Inadequate expertise and skills in managing security investments.;Time and effort required;Disruption to current operations and processes;Compatibility with existing systems;uncertainty about the benefits;Resistance to change;Other",
                            "Unwilling;Slightly willing;Moderately willing;Significantly willing",
                            "Nothing extra;A little more (e.g. up to 5%);Moderately more (e.g. 5-10%);Significantly more (e.g. over 10%)",
                            "Security;Cost;Usability",
                            "Prioritising security;Tend towards prioritising security;Balanced priority;Tend towards cost saving;Cost saving",
                            "Unimportant;Somewhat important;Important",
                            "Weak;Whatever the default is;Hardened;Don’t know",
                            "Familiar with it;Heard of it and understand the concept;Heard of it, but do not have a clear understanding;Not heard of it",
                            "Marginally;Significantly;To a tangible but unspecified degree;Would not adopt",
                            "Robustness and effectiveness of security measures;Compliance with industry standards and regulations;Integration with the existing technology infrastructure;Scalability and flexibility to adapt to current and future security threats;Ease of implementation;Vendor reputation and trust worthiness;Cost and return on investment;Other",
                            "Yes;No;Unsure;N/A",
                            "Yes;No;Partially;N/A",
                            "Increased senior management support;Additional technical capability;Investment;Evidence of security vulnerability;Experience of security breaches;Customer / client demand;Industry recognition (e.g. kitemark);Regulatory requirement;N/A;Other"
                        ]


