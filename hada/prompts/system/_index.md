# system

```
├── 📝 _index.md
├── 📄 hadaV1.txt
├── 📄 hadaV2.txt
├── 📄 hadaV3.txt
├── 📄 hadaV4.txt
├── 📄 hadaV5.txt
├── 📄 hadaV6.1.txt
├── 📄 hadaV6.2.txt
└── 📄 hadaV6.3.txt
```

All system prompt for Hada
-

V1 - First system prompt ever created
- Too complex, instruccions not clear

V2 - Second version improving the instruccions of V1
- Instruccions are clear, but the skel is not well defined

V3 - Improved more the instruccions and the skel of the prompt
- Made the prompt more clearer and super detailed, but it's way too long for the model to handle

V4 - After the last flaw, the prompt was cut
- Reduced the prompt like 60%, mantaining the core instruccions and important things, still clear and works

V5 - New version after trying V4 for a while, this version is not meant to be used it's just a extended and detailed version for next ones
- Changed to english and improved the skel with more detailed sections and improved text, this version is better for most models

V6 - This version will be a group of subversions, made by different AIs to simplify and convert the V5 shorter
- V6.1 - ChatGPT 5.4 Thinking       - 1195/1569 -> -23,84%
- V6.2 - Gemini 3.1 Pro Thinking    - 0927/1569 -> -40,92%
- V6.3 - Claude Sonnet 4.6 Thinking - 1011/1569 -> -35,56%

Prompt used ->
```
## Task

I will give you a prompt. Your job is to shorten it by about 50% in characters, aiming for around 800 characters if possible.

## Instructions

- Keep all important sections, parts, and instructions.
- Preserve the same markdown format.
- Do not use other formats.
- You may rewrite, summarize, reorganize, or change wording if it helps shorten it.
- Do not remove key information or change the original intent of the prompt.
- Make the result clear, simple, and easy to follow.
- Keep in mind it will be used with a small local model, such as Qwen3.5 9B, so avoid complex or overly technical wording.

## Final goal

Return a shorter version of the prompt while keeping its structure, relevant instructions, and original purpose.

## Expected response

- Output only the final shortened prompt.
- Do not add explanations, comments, or extra text.
- Keep the content in markdown inside a code block.
```

V7 -