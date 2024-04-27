# SLAs
**Service Level Agreements (SLAs):**
   - **Definition:** SLAs are formal agreements between a service provider and a customer that outline the expected level of service. They usually include metrics such as uptime, response time, and resolution time.
   - **Responsibilities:**
     - **Defined by Executive Management:** The overall objectives and parameters of the SLA are typically defined by executive management in collaboration with key stakeholders. This includes setting targets for service quality and availability that align with business goals and customer expectations.
     - **Technical Engineers' Role:** Technical engineers play a crucial role in ensuring that the services meet the requirements outlined in the SLA. They are responsible for implementing, monitoring, and maintaining the systems and processes necessary to achieve the agreed-upon service levels.
   - **Example:** A cloud service provider offers an SLA guaranteeing 99.99% uptime for their platform. This means that they commit to ensuring that their service will be available for at least 99.99% of the time within a specified period, such as a month or a year. If they fail to meet this uptime guarantee, they may offer compensation or credits to the customer.
   - **Example 2:** Alternatively, could also work in clauses to handle unplanned downtime outages like below:
     - Cloud Service Company X commits to restoring service within 1 hour (60 minutes) of detecting the outage.
     - Company X further guarantees that in the event of prolonged downtime beyond 1 hour, compensatory measures such as service credits or refunds will be provided to Company Y.
     - TL:DR we want 24/7 uptime but if there is an issue it needs to be resolved within 1 hour or there will be consequences.
     - SLAs are a binding agreement between a service provider and 1 or more customers


# SLOs
**Service Level Objectives (SLOs):**
   - **Definition:** SLOs are specific, measurable goals set for individual aspects of a service, such as response time, availability, or throughput. They are used to define the acceptable level of performance for a service.
   - **Responsibilities:**
     - **Defined by Executive Management:** While executive management may provide input on overall business objectives and priorities, SLOs are often defined by technical teams in collaboration with stakeholders who understand the technical aspects of the service. Executive management may review and approve these objectives to ensure they align with broader business goals.
     - **Technical Engineers' Role:** Technical engineers are primarily responsible for setting realistic and achievable SLOs based on the capabilities of the systems and infrastructure they manage. They monitor performance against these objectives and take corrective actions when necessary to meet or exceed them.
   - **Example:** A software-as-a-service (SaaS) company sets an SLO for their API response time, aiming for 95% of requests to be processed within 100 milliseconds. This means that they have defined a performance target for the speed at which their API responds to incoming requests. They monitor their system continuously to ensure that it meets or exceeds this response time target.
   - SLOs are specific, measurable KPIs set by a service provider for a specific service of theirs

# SLIs
**Other Terminology:**
   - **Service Level Indicators (SLIs):** SLIs are specific metrics used to measure the performance of a service. They provide the data needed to assess whether SLOs and SLAs are being met.
   - **Error Budgets:** Error budgets represent the acceptable level of service degradation or downtime within a given timeframe. They are often used in conjunction with SLOs to balance the need for innovation and reliability.
   - **Example:** A website hosting company uses SLIs such as server response time, error rate, and request throughput to measure the performance of their hosting service. They collect data on these metrics continuously and use them to evaluate the health and reliability of their infrastructure.

