This is a project made for the CAP: 6135 Software and Malware Volnerability Analysis class. 

Our project uses the MM-SafetyBench dataset compiled by Liu et al. https://github.com/isXinLiu/MM-SafetyBench/tree/main
and tests advanced reasoning MLLMs such as Grok, GPT-4o, and Claude 3.7 Sonnet on their safety alignment and how often they refuse to answer harmful questions. 

We specifically tested the StableDiffusion + Typography prompts which were most successful by extracting the text prompt and putting then in a .txt file. Then copying the text and image and pasting it into Monica. 

Warning: a lot of customization can applied in terms of window names it looks for and where it clicks on the sceen, as such this code is for viewing ONLY. 
Getting this code to run in your environment or on your screens will be difficult due to the nature of pyautogui.
