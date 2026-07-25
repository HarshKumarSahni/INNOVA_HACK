prompt_templates = {
    "MTF": """Match the Following type
topics - 
{topics}

difficulty - MODERATE, EXTREMELY ANALYTICAL- each question should be distinct and dont follow the same kind of pattern for each question.
no direct applications. i want them to be really analytical, ones that take several seconds of thought atleast
so please give appropriately tough questions
answer key: {answer_key}
arrange the options such that the answer key is true. make sure that the answer key ive provided is absolutely correct, shows in the questions you give, and matches correctly with the options, solution and the hence line. create {num} - Match The Following type questions like this - very {exam} type, and very analytical. a lot longer and better explanation and dont type anything like topic name or intro etc. just what i asked. remember to add the hence line at the end of each solution. Check for any discrepancies or issues with the question, answer key and solutions. 
make sure to follow the format to the letter. make sure you generate {num} questions, one for each topic, make sure that all the options provided are distinct from each other intraquestion, and also make sure that the correct option is distinct interquestion. there should be variations in the correct options. make sure that the option that the answer key points to matches with the solution. Check if any options are wrongly marked or any options are similar to each other - check each 50 times before sending it. Make sure that you dont add any extra text before or after, There should only be Question Starting, Question, Answer Key, Solution and Hence line for the {num} questions and no other text. make sure to start every question with "--Question Starting--", this is extremely important, make sure that happens, and use this VERY EXACT format -

--Question Starting--
Match the following network types with their most appropriate characteristics:
1. Network Type	Characteristic
I.	LAN	A.	Covers a metropolitan area like a city
II.	MAN	B.	Suitable for intercontinental communication
III.	WAN	C.	Typically uses Ethernet technology
IV.	PAN	D.	Operates within the range of a person
Choose the correct answer from the options given below:
(1)	I-C, II-A, III-B, IV-D
(2)	I-C, II-D, III-A, IV-B
(3)	I-B, II-C, III-A, IV-D
(4)	I-B, II-A, III-D, IV-C
Answer Key: 1	
Solution:	
•	LAN: Local Area Network typically uses Ethernet or Wi-Fi and operates over a small area like an office or campus.
•	MAN: Metropolitan Area Network spans across a city, linking multiple LANs, often via fiber optics or wireless microwave transmission.
•	WAN: WAN Wide Area Network connects networks over large geographical areas, often intercontinental, e.g., the Internet.
•	PAN: Personal Area Network is a short-range network around a person, using Bluetooth or USB connections, for devices like smartphones, smartwatches, etc.
Hence, Option (1) is the right answer.

--Question Starting--
2. Match the following components of an SRS document with their correct descriptions :
SRS Document	Description
I.	Functional Requirements	A.	Constraints on resources such as response time
II.	Non-Functional Requirements	B.	What the system should do in terms of behavior
III.	External Interface Requirements	C.	Describes interactions with hardware/software
IV.	Design Constraints	D.	Limitations on tools, standards, or implementation
Choose the correct answer from the options given below:
(1)	I-B, II-A, III-C, IV-D
(2)	I-C, II-D, III-A, IV-B
(3)	I-B, II-C, III-A, IV-D
(4)	I-A, II-C, III-B, IV-D
Answer Key: 1	
Solution:
•	Functional Requirements: It defines what the system should do, e.g., "The system shall allow users to log in."
•	Non-Functional Requirements: It specifies quality attributes, like performance, reliability, response time, etc.
•	External Interface Requirements: Include how the system interacts with hardware, users, or other software systems.
•	Design Constraints: Define restrictions on development, such as using a particular database, language, or adhering to specific standards.
Hence, Option (1) is the right answer.
""",

    "2S": """2 statement type
topics - 
{topics}
difficulty - MODERATE, EXTREMELY ANALYTICAL- each question should be distinct and dont follow the same kind of pattern for each question.
no direct applications. i want them to be really analytical, ones that take several seconds of thought atleast
so please give appropriately tough questions
answer key: {answer_key}
arrange the options such that the answer key is true. make sure you generate exactly {num} questions, one for each topic, make sure that the answer key ive provided is absolutely correct, shows in the questions you give, and matches correctly with the options, solution and the hence line. 
create {num} - 2 statement type questions like this - very {exam} type, and very analytical. a lot longer and better explanation and dont type anything like topic name or intro etc. just what i asked. remember to add the hence line at the end of each solution. Check for any discrepancies or issues with the question, answer key and solutions. Check if any options are wrongly marked or any options are similar to each other - check each 50 times before sending it. Make sure that you dont add any extra text before or after, There should only be Question Starting, Question, Answer Key, Solution and Hence line for the {num} questions and no other text. make sure to start every question with "--Question Starting--", this is extremely important, make sure that happens, and use this VERY exact format -

--Question Starting--
1. Consider the following two statements related to parsing techniques:
Statement I: LL(1) parsers cannot handle left-recursive grammars and rely on predictive parsing using a single lookahead symbol.
Statement II: LR parsers perform better than LL parsers in terms of grammar acceptance because they can handle a wider class of context-free grammars including left-recursive ones.
In light of the above statements, choose the correct answer from the options given below:
(1)	Both Statement I and Statement II are correct
(2)	Both Statement I and Statement II are incorrect
(3)	Statement I is correct but Statement II is incorrect
(4)	Statement I is incorrect but Statement II is correct
Answer Key: 1	
Solution:
•	Statement I(Correct): LL(1) parsers use top-down parsing with one-symbol lookahead. They fail on left-recursive grammars because recursive calls lead to infinite loops (e.g., A → Aα | β). Hence, left recursion must be eliminated for LL(1) grammars.
•	Statement II(Correct): LR parsers (including SLR, LALR, and canonical LR) use bottom-up parsing. They can handle left recursion, left factoring, and more complex grammar constructs. Thus, they accept a strictly larger set of context-free grammars than LL parsers.
Hence, Option (1) is the right answer.

--Question Starting--
2. Consider the following statements:
Statement I: A queue can be efficiently implemented using two stacks, but the time complexity of the enqueue and dequeue operations may vary based on the chosen strategy.
Statement II: A circular queue overcomes the limitation of a linear queue by reusing vacant spaces created after dequeue operations, thereby optimizing memory usage.
(1)	Both Statement I and Statement II are correct
(2)	Both Statement I and Statement II are incorrect
(3)	Statement I is correct but Statement II is incorrect
(4)	Statement I is incorrect but Statement II is correct
Answer Key: 1
Solution:
•	Statement I(Correct): A queue can be implemented using two stacks:
One strategy pushes all elements during enqueue, and performs stack reversal during dequeue (or vice versa).
The time complexity for either operation can be amortized O(1) in certain strategies, but not always.
•	Statement II(Correct): A circular queue allows reusing the empty spaces in the array once front moves forward, unlike a linear queue that wastes space after repeated dequeue operations. This optimizes memory and is widely used in buffer implementations.
Hence, Option (1) is the right answer.""",

    "3S" : """3 statement type
topics - 
{topics}
difficulty - MODERATE, EXTREMELY ANALYTICAL- each question should be distinct and dont follow the same kind of pattern for each question.
no direct applications. i want them to be really analytical, ones that take several seconds of thought atleast
so please give appropriately tough questions
answer key: {answer_key}
arrange the options such that the answer key is true. make sure you generate exactly {num} questions, one for each topic, make sure that the answer key ive provided is absolutely correct, shows in the questions you give, and matches correctly with the options, solution and the hence line.  
create {num} - 3 statement type questions, one from each topic - very {exam} computer science type, and very analytical.  Check for any discrepancies or issues with the question, answer key and solutions. Check if any options are wrongly marked or any options are similar to each other - check each 50 times before sending it. Make sure that you dont add any extra text before or after, There should only be Question Starting, Question, Answer Key, Solution and Hence line for the {num} questions and no other text. remember to add the hence line at the end of each solution. arrange the options such that the answer key is true. very very long and better explanation and dont type anything like topic or intro etc. just what i asked. - make sure to start every question with "--Question Starting--", this is extremely important, make sure that happens, and use this VERY exact format - 

--Question Starting--
1. Which of the following statements about firewalls and intrusion detection systems are correct?
I.	A firewall can prevent unauthorized access from outside the network but not within it.
II.	Intrusion Detection Systems (IDS) can take automatic action to block malicious activity.
III.	Stateful firewalls monitor the full state of active connections.
Which of the following is correct?
(1)	I and II only
(2)	I and III only
(3)	II and III only
(4)	All of the above
Answer Key: 2
Solution:	
•	Statement I(Correct): Firewalls primarily inspect incoming/outgoing traffic but can't detect internal attacks (e.g., an insider attack).
•	Statement III(Correct): Stateful firewalls keep track of the connection state and can apply rules accordingly.
•	Statement II(Incorrect): This describes an Intrusion Prevention System (IPS), not IDS. IDS is passive, alerts admins but does not block.
Hence, Option (2) is the right answer.

--Question Starting--
2. Consider the following three statements related to Registers and Counters:
I.	A 4-bit Johnson counter cycles through 2⁴ = 16 distinct states before repeating.
II.	In a ring counter with n flip-flops, the number of states is exactly n.
III.	A parallel-in parallel-out (PIPO) register allows simultaneous loading and reading of all bits.
Which of the following is correct?
(1)	I and II only
(2)	I and III only
(3)	II and III only
(4)	All of the above
Answer Key: 3
Solution:	
•	Statement II(Correct): A ring counter is a circular shift register with only one bit set (1) and all others cleared (0).
For n flip-flops, the ring counter cycles through n unique states.
Example: For n = 4, valid states: 1000 → 0100 → 0010 → 0001 → (back to 1000)
•	Statement III(Correct): A Parallel-In Parallel-Out (PIPO) register:
Parallel-In: All bits of data are loaded into the register simultaneously.
Parallel-Out: All bits are read simultaneously.
It is used in high-speed data handling.
•	Statement I(Incorrect): A 4-bit Johnson counter (also called a twisted ring counter) goes through 2n = 8 states, not 16.
General formula for n flip-flops, Johnson counter → 2n states.
For 4 bits: 2 × 4 = 8 unique states.
A normal binary counter would go through 2⁴ = 16 states, but not a Johnson counter.
Hence, Option (3) is the right answer.""",

    "4S": """4 statement type
topics - 
{topics}
difficulty - MODERATE, EXTREMELY ANALYTICAL- each question should be distinct and dont follow the same kind of pattern for each question.
no direct applications. i want them to be really analytical, ones that take several seconds of thought atleast
so please give appropriately tough questions
answer key: {answer_key}
arrange the options such that the answer key is true. make sure you generate exactly {num} questions, one for each topic, make sure that the answer key ive provided is absolutely correct, shows in the questions you give, and matches correctly with the options, solution and the hence line.  
create {num} - 4 statement type questions, one from each topic - very {exam} computer science type, and very analytical.  Check for any discrepancies or issues with the question, answer key and solutions. Check if any options are wrongly marked or any options are similar to each other - check each 50 times before sending it. Make sure that you dont add any extra text before or after, There should only be Question Starting, Question, Answer Key, Solution and Hence line for the {num} questions and no other text. remember to add the hence line at the end of each solution. arrange the options such that the answer key is true. very very long and better explanation and dont type anything like topic or intro etc. just what i asked. - make sure to start every question with "--Question Starting--", this is extremely important, make sure that happens, and use this VERY exact format - 

--Question Starting--
1. Which of the following statements about FCFS (First Come First Serve) scheduling are correct?
I.	FCFS scheduling can lead to convoy effect.
II.	Average waiting time is minimum in FCFS.
III.	FCFS scheduling is non-preemptive.
IV.	Processes are scheduled in the order they arrive.
Choose the correct answer from the options given below:
(1)	I, II, and III only
(2)	II and III only
(3)	I, III, and IV only
(4)	All of the above
Answer Key: 3
Solution:
•	Statement I(Correct): Convoy effect happens when short processes wait for a long process in FCFS.
•	Statement III(Correct): FCFS is non-preemptive.
•	Statement IV(Correct): FCFS schedules purely based on arrival time.
•	Statement II(Incorrect): FCFS does not guarantee minimum average waiting time (SJF does that).
Hence, Option (3) is the right answer.

--Question Starting--
2. Which of the following statements about Windows OS internals and management features are correct?
I.	Windows uses a hybrid kernel that combines features of monolithic and microkernel architectures.
II.	Windows Task Scheduler uses a preemptive priority-based scheduling policy for managing processes.
III. NTFS (New Technology File System) in Windows does not support file-level security or journaling.
IV.	Windows services can only be initiated by the user manually via the GUI and not during system boot.
Choose the correct answer from the options given below:
(1)	I, and II only
(2)	II and IV only
(3)	II, III, and IV only
(4)	All of the above
Answer Key: 1
Solution:
•	Statement I(Correct): Windows uses a hybrid kernel, which combines features of both monolithic kernels (like direct hardware interaction) and microkernels (like modularity). It's not strictly microkernel or monolithic, but merges performance with modularity.
•	Statement II(Correct): Windows uses a preemptive, priority-based scheduling algorithm for threads. Threads with higher priority preempt lower-priority ones and the scheduler also considers quantum expiration for fair CPU distribution.
•	Statement III(Incorrect): NTFS supports file-level security via Access Control Lists (ACLs), journaling for fault tolerance and recoverability, compression, encryption, and disk quotas.
•	Statement IV(Incorrect): Windows services can be set to start automatically during system boot (e.g., DHCP Client, Windows Update), and can also be manually started via GUI (Services.msc) or command-line (sc, net start). Hence, not limited to manual start only.
Hence, Option (1) is the right answer.""",

    "5S": """5 statement type
topics - 
{topics}

difficulty - *EXTREMELY* HARD, *EXTREMELY* ANALYTICAL - each question should be distinct and dont follow the same kind of pattern for each question.
when i ask for extremely difficult questions, i MEAN extremely difficult. no direct applications.
i want them to be really analytical, ones that take several seconds of thought atleast
so please give appropriately tough questions
answer key: {answer_key}
arrange the options such that the answer key is true. make sure you generate exactly {num} questions, one for each topic, make sure that the answer key ive provided is absolutely correct, shows in the questions you give, and matches correctly with the options, solution and the hence line.  
create {num} - 5 statement type questions, one from each topic - very {exam} computer science type, and very analytical.  Check for any discrepancies or issues with the question, answer key and solutions. Check if any options are wrongly marked or any options are similar to each other - check each 50 times before sending it. Make sure that you dont add any extra text before or after, There should only be Question Starting, Question, Answer Key, Solution and Hence line for the {num} questions and no other text. remember to add the hence line at the end of each solution. arrange the options such that the answer key is true. very very long and better explanation and dont type anything like topic or intro etc. just what i asked. - make sure to start every question with "--Question Starting--", this is extremely important, make sure that happens, and use this VERY exact format - 

--Question Starting--
1. Consider the following statements regarding pipeline and vector processing:
I.	In a non-pipelined processor, the total execution time for n instructions is proportional to n × k, where k is the number of stages.
II.	Vector processors use deep pipelines and are optimized for operations on large arrays.
III. Instruction-level parallelism (ILP) is primarily exploited in scalar pipeline architectures, not in vector processors.
IV.	Pipeline hazards can be categorized as structural, data, and control hazards.
V.	In an ideal pipelined processor, n instructions complete in n + k - 1 cycles, assuming no stalls.
Choose the correct answer from the options given below:
(1)	I, II, and III only
(2)	I, II, IV and V only
(3)	I, II, III and V only
(4)	I, III, IV and V only
Answer Key: 2
Solution:
•	Statement I(Correct): In a non-pipelined processor, each instruction must go through all stages sequentially. So, time to execute n instructions = n x k clock cycles.
No overlap of stages = linear increase in time.
•	Statement II(Correct): Vector processors use deep pipelines and vector registers. They're optimized for data-parallel tasks such as array processing, matrix operations, etc.
For example: Cray vector machines.
•	Statement IV(Correct): There are three types of pipeline hazards:
Structural hazard - due to resource conflicts
Data hazard - due to data dependencies
Control hazard - due to branch/instruction flow changes
•	Statement V(Correct): In ideal pipelining, time to execute n instructions = n + k - 1 cycles, where k is the number of stages. This accounts for pipeline filling and draining.
•	Statement III(Incorrect): Instruction-Level Parallelism (ILP) is also exploited in vector processors, especially pipelined vector units. Scalar pipelines exploit ILP via superscalar/multicycle techniques, but vector processors also use ILP efficiently for vector operations. Hence, the distinction is not exclusive.
Hence, Option (2) is the right answer.

--Question Starting--
2. Consider the following statements about various AI algorithms and techniques:
I.	In A* algorithm, the evaluation function f(n) = g(n) + h(n) ensures optimality only if h(n) is admissible and consistent.
II.	Hill Climbing algorithm is complete and guarantees a global optimum if the heuristic function is monotonic.
III.	Minimax algorithm assumes that the opponent plays optimally and is mainly used in two-player deterministic games.
IV.	Alpha-Beta pruning does not affect the final outcome of minimax but reduces the number of nodes evaluated.
V.	Genetic Algorithms operate based on the principles of reinforcement learning to find optimal solutions.
Choose the correct answer from the options given below:
(1)	I, II, and III only
(2)	I, II, IV and V only
(3)	I, III and IV only
(4)	I, III, IV and V only
Answer Key: 3
Solution:
•	Statement I(Correct): In A* search, the heuristic h(n) must be admissible (never overestimates cost) and consistent (also known as monotonic) to ensure optimality. This is a foundational requirement for A* to always find the shortest path.
•	Statement III(Correct): Minimax is used in two-player zero-sum games and assumes that both players play optimally. The opponent's optimal moves are simulated to determine the best move for the player.
•	Statement IV(Correct): Alpha-Beta pruning improves efficiency of minimax by pruning branches that won't affect the final decision. It doesn't change the result, only reduces search time.
•	Statement II(Incorrect): Hill Climbing is not complete and often gets stuck in local maxima, even with a monotonic heuristic. It lacks backtracking and may fail even when a solution exists.
•	Statement V(Incorrect): Genetic Algorithms are based on evolutionary principles like selection, crossover, and mutation. They are not based on reinforcement learning, which uses reward signals to learn policies.
Hence, Option (3) is the right answer.""",

    "SL": """Single liner type
topics - 
{topics}
difficulty - MODERATE, EXTREMELY ANALYTICAL- each question should be distinct and dont follow the same kind of pattern for each question.
no direct applications. i want them to be really analytical, ones that take several seconds of thought atleast
so please give appropriately tough questions
answer key: {answer_key}
arrange the options such that the answer key is true. make sure you generate exactly {num} questions, one for each topic, make sure that the answer key ive provided is absolutely correct, shows in the questions you give, and matches correctly with the options, solution and the hence line. 
Create {num} - single liner type questions like this, one question should be from each topic provided - very {exam} type, and very analytical. a lot longer and better explanation and dont type anything like topic name or intro etc. just what i asked. remember to add the hence line at the end of each solution. Check for any discrepancies or issues with the question, answer key and solutions. Check if any options are wrongly marked or any options are similar to each other - check each 50 times before sending it. Make sure that you dont add any extra text before or after, There should only be Question Starting, Question, Answer Key, Solution and Hence line for the {num} questions and no other text. make sure to start every question with "--Question Starting--", this is extremely important, make sure that happens, and use this VERY exact format -

--Question Starting--
1. A team of developers built an e-commerce web application using the MERN stack. During staging, they conducted performance testing using JMeter and identified issues with concurrent request handling. The security team later flagged improper session termination and vulnerable endpoints. Before production deployment, they integrated the CI/CD pipeline with automated testing tools and containerized the app using Docker. 
Which of the following doesn't address the issues raised in the testing and deployment stages?
(1)	Implementing rate-limiting and horizontal scaling can improve concurrent request handling.
(2)	CI/CD pipelines alone are sufficient to prevent all security vulnerabilities.
(3)	Docker ensures consistent environments, aiding in reproducible deployment.
(4)	Proper session management and input validation help reduce attack surfaces.
Answer Key: 2
Solution:
•	Option 1 (Correct): JMeter flagged concurrency issues; rate-limiting prevents abuse, and horizontal scaling (adding servers/containers) enhances parallel processing.
•	Option 3 (Correct): Containerization guarantees that the application runs the same across environments, reducing “works-on-my-machine” issues.
•	Option 4 (Correct): Secure session handling (e.g., logout, timeout) and input validation (e.g., sanitization) are crucial to defend against threats like XSS, CSRF, and injection attacks.
•	Option 2 (Incorrect): CI/CD automates testing and deployment, but cannot guarantee complete security unless integrated with security scanners, code audits, or DevSecOps practices.
Hence, Option (2) is the right answer.


--Question Starting--
2. A university maintains a single table STUDENT_COURSE with fields: StudentID, StudentName, CourseID, CourseName, InstructorName. It was observed that if a student takes multiple courses, their name and ID are repeated, and if a course is taught by different instructors over time, course-instructor combinations also repeat. After complaints about data inconsistency and redundancy, a normalization review was proposed.
Which of the following normalization strategies would best eliminate the redundancy and anomalies described in the above case?
(1)	Decompose the table into separate relations for Students and Courses to achieve Second Normal Form (2NF)
(2)	Keep the table intact, but enforce composite keys to satisfy First Normal Form (1NF)
(3)	Separate instructor data to eliminate transitive dependencies and achieve Third Normal Form (3NF)
(4)	Apply Boyce-Codd Normal Form (BCNF) directly to remove all types of multivalued dependencies
Answer Key: 3
Solution:
•	Option 3 (Correct): This is the most suitable step. Here, InstructorName is dependent on CourseName, and not directly on the primary key. This is a transitive dependency, and to move to 3NF, we should separate course-instructor mapping into another table.
•	Option 1 (Incorrect): This only eliminates partial dependencies, which occur when non-prime attributes are dependent on part of a composite key. But in the case, InstructorName depends on CourseName, which is a transitive dependency, not a partial one.
•	Option 2 (Incorrect): 1NF only ensures atomicity of values and removes repeating groups. This won't solve redundancy or update anomalies in the case described.
•	Option 4 (Incorrect): BCNF handles anomalies due to overlapping candidate keys, but the case here is about transitive dependencies, not key overlaps. Also, multivalued dependencies are handled in Fourth Normal Form (4NF), not BCNF.
Hence, Option (3) is the right answer.""",

    "AR": """AR
topics - 
{topics}
difficulty - MODERATE, EXTREMELY ANALYTICAL- each question should be distinct and dont follow the same kind of pattern for each question.
no direct applications. i want them to be really analytical, ones that take several seconds of thought atleast
so please give appropriately tough questions
answer key: {answer_key}
arrange the options such that the answer key is true. make sure you generate exactly {num} questions, one for each topic, make sure that the answer key ive provided is absolutely correct, shows in the questions you give, and matches correctly with the options, solution and the hence line.  
Check for any discrepancies or issues with the question, answer key and solutions. Check if any options are wrongly marked or any options are similar to each other - check each 50 times before sending it. Make sure that you dont add any extra text before or after, There should only be Question Starting, Question, Answer Key, Solution and Hence line for the {num} questions and no other text. arrange the options such that the answer key is true. remember to add the hence line at the end of each solution. 
create {num} assertion reasoning type questions like this - very {exam} type, and very analytical. a lot longer and better explanation and dont type anything like topic name or intro etc. just what i asked. make sure to start every question with "--Question Starting--", this is extremely important, make sure that happens, and use this VERY EXACT format - format -

--Question Starting--
1. Given below are two statements, one is labelled as Assertion (A) and the other is
labelled as Reason (R).
Assertion (A): If a system is deadlocked, no process can proceed further until resources
are released. Reason (R): In a deadlock, each process holds some resources and waits indefinitely for others, leading to a circular wait. In light of the above statements, choose the most appropriate answer from the options
below:
(1) Both Assertion and Reason are correct, and Reason is the correct explanation of Assertion. 
(2) Both Assertion and Reason are correct, but Reason is not the correct explanation of Assertion. 
(3) Assertion is correct, but Reason is incorrect. 
(4) Assertion is incorrect, but Reason is correct. 
Answer Key: 1
Solution: 
•	Assertion (A) is correct: In deadlock, processes are stuck forever unless an external action (like killing a process) is taken.
•	Reason (R) is correct: Circular wait is one of the four Coffman conditions necessary for adeadlock.
•	So, Assertion and Reason are both correct, and Reason is the correct explanation of Assertion.
Hence, Option (1) is the right answer

--Question Starting--
2. Given below are two statements, one is labelled as Assertion (A) and the other is labelled as Reason (R).
Assertion (A): Dead code elimination helps in reducing the size of the executable file.
Reason (R): Dead code refers to program statements that are syntactically incorrect and cause compilation errors.
In light of the above statements, choose the most appropriate answer from the options below:
(1)	Both Assertion and Reason are correct, and Reason is the correct explanation of Assertion.
(2)	Both Assertion and Reason are correct, but Reason is not the correct explanation of Assertion.
(3)	Assertion is correct, but Reason is incorrect.
(4)	Assertion is incorrect, but Reason is correct.
Answer Key: 3
Solution:
•	Assertion (A) is correct: Dead code elimination is a form of code optimization where code that does not affect the program output (such as unreachable statements or unused variables) is removed. This indeed helps reduce the size of the executable and potentially enhances performance.
•	Reason (R) is incorrect: Dead code is not code that causes compilation errors. It refers to valid but unused code, such as:
int a = 5;
a = 10;  // if 'a' is never used afterward, the assignment is dead code.
•	So, Assertion is correct, but Reason is incorrect.
Hence, Option (3) is the right answer.""",

    "CS" : """Case Study
topic - 
{topics}
arrange the questions such that the answer key is - {answer_key}
difficulty - MODERATE, EXTREMELY ANALYTICAL- each question should be distinct and dont follow the same kind of pattern for each question.
no direct applications. i want them to be really analytical, ones that take several seconds of thought atleast
so please give appropriately tough questions
{num} more case study type questions like this - a lot harder, very very analytical. very {exam} type. remember to add the hence line at the end - important. longer and better explanation and dont type anything like topic or intro etc. just what i asked. Check for any discrepancies or issues with the question, answer key and solutions. Check if any options are wrongly marked or any options are similar to each other - check each 50 times before sending it. Make sure that you dont add any extra text before or after, There should only be Question Starting, Question, Answer Key, Solution and Hence line for the {num} questions and no other text. 

make sure you create exactly {num} questions, one from each topic and make sure to start every question with "--Question Starting--", this is extremely important, make sure that happens and use this exact format - format -

--Question Starting--
1. A public service campaign utilizes television commercials, social media, and community health workers to disseminate information about the importance of vaccination for children and to address misinformation about vaccine safety. This initiative aims to improve child health outcomes and reduce the prevalence of preventable diseases.

According to the principles of development communication, which critical societal issue is this campaign primarily addressing?
(1) Population growth
(2) Health disparities
(3) Human rights violations
(4) Rural and tribal development
Answer Key: (2) 
Solution:
Option (2) is correct: The public service campaign focuses on disseminating crucial health information regarding childhood vaccinations and countering misinformation. The primary goal is to improve child health outcomes and reduce the occurrence of preventable diseases. This directly aligns with the aims of development communication in addressing health disparities by promoting health awareness, ensuring access to vital health knowledge, and ultimately working towards equitable health outcomes for children.
Option (1) is incorrect:  The population growth, is not the central focus of a vaccination campaign, although child health can indirectly influence population dynamics over time.
Option (3) is incorrect: The human rights violations, while important, is not the primary issue being tackled by a vaccination campaign. Access to healthcare can be considered a human right, but the campaign's direct focus is on health and disease prevention. 
Option (4) is incorrect: The rural and tribal development, while these communities might be specific targets for vaccination efforts due to potential disparities in access, the overarching societal issue being addressed by a widespread public service campaign on vaccination is broader than just these specific populations. The campaign aims to improve child health across all segments of society.
Hence, the correct answer is Option (2).""",

"CH" : """Chronology
topics - 
{topics}
answer keys - {answer_key}
difficulty - MODERATE, EXTREMELY ANALYTICAL- each question should be distinct and dont follow the same kind of pattern for each question.
no direct applications. i want them to be really analytical, ones that take several seconds of thought atleast
so please give appropriately tough questions
arrange the options such that the answer key is true. create {num} chronology type questions like this - very {exam} type, and very analytical. a lot longer and better explanation and dont type anything like topic name or intro etc.  just what i asked. remember to add the hence line at the end - important.  Check for any discrepancies or issues with the question, answer key and solutions. Check if any options are wrongly marked or any options are similar to each other - check each 50 times before sending it. Make sure that you dont add any extra text before or after, There should only be Question Starting, Question, Answer Key, Solution and Hence line for the {num} questions and no other text. 
make sure you create exactly {num} questions, one from each topic and make sure to start every question with "--Question Starting--", this is extremely important, make sure that happens and use this VERY exact format -

--Question Starting--
1. What is the correct physiological sequence of events involved in the absorption and regulation of sodium within the human body?
I. Sodium Movement via Na⁺/K⁺ Pump
II. Co-transport with Nutrients  
III. Reabsorption by Kidneys
IV. Absorption Driven by Bulk Flow
V. Hormonal Control and Excretion 
Choose the correct answer from the options given below:
(1) I, III, II, V, IV
(2) II, I, IV, III, V 
(3) II, I, III, IV, V
(4) I, II, III, V, IV
Answer Key: (2)
Solution:

Statement II - The initial site of sodium absorption and control is the small intestine. The sodium is absorbed through co-transport processes, with glucose or amino acids, particularly in the duodenum and jejunum.
Statement I - The Na+/K+-ATPase pump actively transports sodium into the bloodstream once it enters intestinal cells, preserving the concentration gradient necessary for further absorption.
Statement IV - The osmotic movement of fluids known as bulk flow play an additional role in sodium absorption by the body.
Statement III - Sodium regulation through the kidney occurs when these organs take up filtered salt following the absorption process.
Statement V - Aldosterone regulates how much sodium the body either keeps or releases depending on its needs thus supporting both fluid stability and proper functions of neurons and muscles.
Hence, the correct answer is Option (2).""",
"FIL":"""fill blanks 
topic - 
{topics}

answer key - {answer_key}
difficulty - MODERATE, EXTREMELY ANALYTICAL- each question should be distinct and dont follow the same kind of pattern for each question.
no direct applications. i want them to be really analytical, ones that take several seconds of thought atleast
so please give appropriately tough questionstype - {exam}
create {num} fill in the blanks type questions like this - very very analytical. and unique. a lot longer and better explanation and dont type anything like topic name or intro etc. just what i asked. remember to add the hence line at the end - important.  Check for any discrepancies or issues with the question, answer key and solutions. Check if any options are wrongly marked or any options are similar to each other - check each 50 times before sending it. Make sure that you dont add any extra text before or after, There should only be Question Starting, Question, Answer Key, Solution and Hence line for the {num} questions and no other text. 
make sure you create exactly {num} questions, one from each topic and make sure to start every question with "--Question Starting--", this is extremely important, make sure that happens and use this VERY exact format  - format - 
 
--Question Starting--
1. Quality Assurance emphasizes ________ defects rather than just detecting them.
(1) Ignoring
(2) Documenting
(3) Preventing
(4) Highlighting
Answer Key: (3)
Solution:
Option (3) is correct. Quality Assurance (QA) focuses on building quality into the process itself to ensure that defects are avoided from the beginning.
Option (1) is incorrect. QA never ignores potential defects; it actively works to eliminate them.
Option (2) is incorrect. Documenting refers to recording information. It does not address the goal - prevention of QA.
Option (4) is incorrect. Highlighting involves pointing out defects after they occur, which is more aligned with Quality Control activities.
Thus, the correct answer is Option (3).""",

"CS" : """Case Study
topic - 
{topics}
arrange the questions such that the answer key is - {answer_key}
difficulty - MODERATE, EXTREMELY ANALYTICAL- each question should be distinct and dont follow the same kind of pattern for each question.
no direct applications. i want them to be really analytical, ones that take several seconds of thought atleast
so please give appropriately tough questions
{num} more case study type questions like this - a lot harder, very very analytical. very {exam} type. remember to add the hence line at the end - important. longer and better explanation and dont type anything like topic or intro etc. just what i asked. Check for any discrepancies or issues with the question, answer key and solutions. Check if any options are wrongly marked or any options are similar to each other - check each 50 times before sending it. Make sure that you dont add any extra text before or after, There should only be Question Starting, Question, Answer Key, Solution and Hence line for the {num} questions and no other text. 

make sure you create exactly {num} questions, one from each topic and make sure to start every question with "--Question Starting--", this is extremely important, make sure that happens and use this exact format - format -

--Question Starting--
1. A public service campaign utilizes television commercials, social media, and community health workers to disseminate information about the importance of vaccination for children and to address misinformation about vaccine safety. This initiative aims to improve child health outcomes and reduce the prevalence of preventable diseases.

According to the principles of development communication, which critical societal issue is this campaign primarily addressing?
(1) Population growth
(2) Health disparities
(3) Human rights violations
(4) Rural and tribal development
Answer Key: (2) 
Solution:
Option (2) is correct: The public service campaign focuses on disseminating crucial health information regarding childhood vaccinations and countering misinformation. The primary goal is to improve child health outcomes and reduce the occurrence of preventable diseases. This directly aligns with the aims of development communication in addressing health disparities by promoting health awareness, ensuring access to vital health knowledge, and ultimately working towards equitable health outcomes for children.
Option (1) is incorrect:  The population growth, is not the central focus of a vaccination campaign, although child health can indirectly influence population dynamics over time.
Option (3) is incorrect: The human rights violations, while important, is not the primary issue being tackled by a vaccination campaign. Access to healthcare can be considered a human right, but the campaign's direct focus is on health and disease prevention. 
Option (4) is incorrect: The rural and tribal development, while these communities might be specific targets for vaccination efforts due to potential disparities in access, the overarching societal issue being addressed by a widespread public service campaign on vaccination is broader than just these specific populations. The campaign aims to improve child health across all segments of society.
Hence, the correct answer is Option (2).""",

"MCQ" : """MSQ

answer key - {answer_key}
topic - {topics}
difficulty - MODERATE, EXTREMELY ANALYTICAL- each question should be distinct and dont follow the same kind of pattern for each question.
no direct applications. i want them to be really analytical, ones that take several seconds of thought atleast
so please give appropriately tough questions
create {num} msq type questions with multiple being selected- very {exam} type . arrange the options such that the answer key is true. longer and better explanation and dont type anything like topic or intro etc. just what i asked. remember that msq type questions' options are always short and of only 1 to 4 words max. remember to add the hence line at the end of each solution.  Check for any discrepancies or issues with the question, answer key and solutions. Check if any options are wrongly marked or any options are similar to each other - check each 50 times before sending it. Make sure that you dont add any extra text before or after, There should only be Question Starting, Question, Answer Key, Solution and Hence line for the {num} questions and no other text. 
make sure you create exactly {num} questions, one from each topic and make sure to start every question with "--Question Starting--", this is extremely important, make sure that happens and use this VERY exact format -

--Question Starting--
23.Which of the following statements about FCFS (First Come First Serve) scheduling are correct?
I.FCFS scheduling can lead to convoy effect.
II.Average waiting time is minimum in FCFS.
III.FCFS scheduling is non-preemptive.
IV.Processes are scheduled in the order they arrive.
Choose the correct answer from the options given below:
(1)I, II, and III only
(2)II and III only
(3)I, III, and IV only
(4)All of the above
Answer Key: 3
Solution:
Statement I (Correct): Convoy effect happens when short processes wait for a long process in FCFS.
Statement II(Incorrect): FCFS does not guarantee minimum average waiting time (SJF does that).
Statement III(Correct): FCFS is non-preemptive.
Statement IV(Correct): FCFS schedules purely based on arrival time.
Hence, the correct answer is Option (3).""",

"NU" : """Numerical Type Questions
topics - 
{topics}
difficulty - MODERATE, EXTREMELY ANALYTICAL- each question should be distinct and dont follow the same kind of pattern for each question.
no direct applications. i want them to be really analytical, ones that take several seconds of thought atleast
so please give appropriately tough questions
answer key: {answer_key}
arrange the options such that the answer key is true. make sure you generate exactly {num} numerical questions, one for each topic, make sure that the answer key ive provided is absolutely correct, shows in the questions you give, and matches correctly with the options, solution and the hence line.  
Check for any discrepancies or issues with the question, answer key and solutions. Check if any options are wrongly marked or any options are similar to each other - check each 50 times before sending it. Make sure that you dont add any extra text before or after, There should only be Question Starting, Question, Answer Key, Solution and Hence line for the {num} questions and no other text. arrange the options such that the answer key is true. remember to add the hence line at the end of each solution. 
create {num} numerical type questions like this - very {exam} type, and very analytical. a lot longer and better explanation and dont type anything like topic name or intro etc. just what i asked. make sure to start every question with "--Question Starting--", this is extremely important, make sure that happens, and use this VERY EXACT format - format -

--Question Starting--
A box contains 5 red, 4 blue, and 3 green balls. If 3 balls are drawn at random without
replacement, what is the probability that all three are of different colors?
(1) 5/11
(2) 7/11
(3) 3/11
(4) None of the above
Answer Key: 3
Solution:
Step 1: Total number of ways to choose 3 balls out of 12
12 Total ways = ( 12 3 )
= 12x11x10 / 3x2x1
= 220
Step 2: Favorable outcomes (1 red, 1 blue, 1 green)
We need:
Choose 1 red out of 5: ( 5 1 ) = 5
Choose 1 blue out of 4: ( 4 1 ) = 4
Choose 1 green out of 3: ( 3 1 )=3
Favorable outcomes = 5:4:3 = 60
Step 3: Required Probability
P(all different colors) = 60/220
= 3/11
Hence, Option (3) is the right answer."""
}