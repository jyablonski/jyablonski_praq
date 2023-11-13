# Software Development Lifecycle

1. **Requirements Gathering and Analysis:**
   - In this stage, project stakeholders, including clients and end-users, collaborate with the development team to gather and document the requirements for the software.
   - The goal is to clearly define the problem the software will solve and the features it needs to have.
   - Rough Cost Estimates are generated.
   - Project Timeline is created

2. **System Design:**
   - During this phase, the architecture and high-level design of the software are created.
   - Software architects create system specifications, which outline the system's structure and components.
   - Design documents are created to provide a blueprint for the development phase.
   - Rough Cost Estimates are generated.
   - If the Product or Application has B2B elements w/ 3rd party engineering teams, they're brought in here at this phase for design feedback & input.
     - Examples:
       - Company A is creating a REST API for Company B to use.
       - Compancy C generates some valuable dataset needed by Company D's new product.

3. **Building:**
   - In this stage, developers write the actual code for the software based on the design documents.
   - Programming languages and tools are used to implement the features and functionality specified in the requirements.
   - Cost is continuing to be monitored.

4. **Testing:**
   - Developer and Engineering Teams build out unit & integration testing
   - Quality assurance (QA) teams conduct various types of system, regression, and user acceptance testing as the product gets iteratively built out.
   - Bugs and issues are identified and addressed, and the software is refined.

5. **Deployment:**
   - Once the software has passed all testing phases, it is deployed to a production environment or made available to end-users.
   - New features or functionality can be put behind feature flags, or behind A / B Testing to present new features to only `x`% of end-users.

6. **Maintenance and Support:**
   - After deployment, the software enters a phase of ongoing maintenance and support.
   - Product or Application is under various monitoring to ensure it's operational and functioning as intended.
   - A constant feedback loop takes place between Customer Success, Product, and Development Teams to manage the balancing act of fixing bugs, managing Tech Debt, and prioritizing new software features.

The Waterfall model is a linear and sequential approach, which means that each phase must be completed before moving on to the next. While it provides a structured and well-documented process, it can be less flexible when it comes to adapting to changing requirements.

There are also other SDLC models, such as the Agile model, which promotes iterative and incremental development, allowing for more flexibility and adaptability throughout the development process. In Agile, the development cycle is divided into smaller iterations, and working software is delivered more frequently.
