# Open Systems Interconnection

Open Systems Interconnection (OSI) is a conceptual framework that standardizes the functions of a communication system into 7 layers. It segments networking tasks into these modular layers to help in understanding and designing the network protocols. The **OSI model** is a theoretical framework, the **TCP/IP model** (a more practical implementation) is widely used in real-world networking.


### **The 7 Layers of the OSI Model**
Each layer serves a specific function and interacts with the layers above and below it.

1. **Physical Layer (Layer 1)**
   - Deals with the **hardware** transmission of raw bit streams over a physical medium (cables, fiber optics, radio waves).
   - Examples: Ethernet cables, Wi-Fi, Bluetooth, hubs, repeaters, cross Atlantic cabling.
   - Basically the transferring of data in its most physical form

2. **Data Link Layer (Layer 2)**
   - Responsible for **framing, addressing (MAC addresses), error detection, and correction**.
   - Divided into **Logical Link Control (LLC)** and **Media Access Control (MAC)** sublayers.
   - Examples: Ethernet, Wi-Fi (802.11), MAC addresses, switches, bridges.
   - The bit you really do not ever need to involve yourself with

3. **Network Layer (Layer 3)**
   - Manages **routing, logical addressing (IP addresses), and packet forwarding**.
   - Determines the best path for data transmission.
   - Examples: IP (Internet Protocol), ICMP (ping), routers.
   - This layer is responsible for translating between host addresses and network addressing to send data across different networks
   - Routers operate at this layer

4. **Transport Layer (Layer 4)**
   - Ensures **end-to-end communication, reliability, and flow control**.
   - Uses protocols like:
     - **TCP (Transmission Control Protocol)** – Reliable, connection-oriented (e.g., web browsing, file transfers).
     - **UDP (User Datagram Protocol)** – Fast, connectionless (e.g., video streaming, VoIP).
   - Examples: TCP, UDP, port numbers.

5. **Session Layer (Layer 5)**
   - Manages and controls **sessions (connections) between applications**.
   - Handles session establishment, maintenance, and termination.
   - Examples: NetBIOS, RPC (Remote Procedure Call).

6. **Presentation Layer (Layer 6)**
   - Responsible for **data translation, encryption, and compression**.
   - Converts data into a format that the application layer can understand.
   - Examples: SSL/TLS (encryption), JPEG, ASCII, MPEG.
   - This layer deals with data compression and encrypting + decrypting data

7. **Application Layer (Layer 7)**
   - The **interface between users and the network**.
   - Provides network services such as **web browsing, email, file transfer**.
   - Examples: HTTP, FTP, SMTP (email), DNS.

The OSI Model provides:

- **Standardization**: Ensures interoperability between different systems and devices.
- **Troubleshooting**: Helps in diagnosing network issues by identifying the affected layer.
- **Modular Design**: Allows protocols to evolve independently within each layer.
