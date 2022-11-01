# PandiBot

Technology: Rasa, Python
Support technology: ngrok (https://ngrok.com/) - if paired with FB only

- Already trained on 500 epochs model available in the models folder.
- Install Rasa inside the project if not already done

Steps to run the chatbot:
1. Open IDE
2. Open two terminals
3. In the first terminal, run the command: "rasa shell"
4. In the second terminal: "rasa run actions"

To know:
- words to be avoided: "nothing", "i dont know", "please"; single-worded asnwers as well
- it is recommended to answer in full sentences when an "open question" occurs (Example: "I sometimes stop by the donuts shop on Fridays")
- it is also recommended to keep answers short when a deny or affirm is expected (Examples: "of course!", "Sure", "nah", "Yes", etc.)

Ran with the following resources:

Intel(R) Core(TM) i9-10900K CPU @ 3.70GHz (20 CPUs), 3.7GHz,
NVIDIA GeForce RTX 2080 SUPER (8GB) and 32GB of installed RAM
