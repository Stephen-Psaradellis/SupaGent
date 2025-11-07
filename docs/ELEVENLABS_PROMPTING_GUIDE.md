# ElevenLabs Agent Prompting Guide

Source: https://elevenlabs.io/docs/agents-platform/best-practices/prompting-guide

## Overview

Effective prompting transforms ElevenLabs Agents from robotic to lifelike. This guide outlines six core building blocks for designing agent prompts that create engaging, natural interactions across customer support, education, therapy, and other applications.

The difference between an AI-sounding and naturally expressive conversational agents comes down to how well you structure its system prompt.

The system prompt controls conversational behavior and response style, but does not control conversation flow mechanics like turn-taking, or agent settings like which languages an agent can speak. These aspects are handled at the platform level.

## Six Building Blocks

Each system prompt component serves a specific function. Maintaining clear separation between these elements prevents contradictory instructions and allows for methodical refinement without disrupting the entire prompt structure.

1. **Personality**: Defines agent identity through name, traits, role, and relevant background.
2. **Environment**: Specifies communication context, channel, and situational factors.
3. **Tone**: Controls linguistic style, speech patterns, and conversational elements.
4. **Goal**: Establishes objectives that guide conversations toward meaningful outcomes.
5. **Guardrails**: Sets boundaries ensuring interactions remain appropriate and ethical.
6. **Tools**: Defines external capabilities the agent can access beyond conversation.

### 1. Personality

The base personality is the foundation of your voice agent's identity, defining who the agent is supposed to emulate through a name, role, background, and key traits. It ensures consistent, authentic responses in every interaction.

- **Identity:** Give your agent a simple, memorable name (e.g. "Joe") and establish the essential identity (e.g. "a compassionate AI support assistant").
- **Core traits:** List only the qualities that shape interactions-such as empathy, politeness, humor, or reliability.
- **Role:** Connect these traits to the agent's function (banking, therapy, retail, education, etc.). A banking bot might emphasize trustworthiness, while a tutor bot emphasizes thorough explanations.
- **Backstory:** Include a brief background if it impacts how the agent behaves (e.g. "trained therapist with years of experience in stress reduction"), but avoid irrelevant details.

### 2. Environment

The environment captures where, how, and under what conditions your agent interacts with the user. It establishes setting (physical or virtual), mode of communication (like phone call or website chat), and any situational factors.

- **State the medium**: Define the communication channel (e.g. "over the phone", "via smart speaker", "in a noisy environment"). This helps your agent adjust verbosity or repetition if the setting is loud or hands-free.
- **Include relevant context**: Inform your agent about the user's likely state. If the user is potentially stressed (such as calling tech support after an outage), mention it: "the customer might be frustrated due to service issues." This primes the agent to respond with empathy.
- **Avoid unnecessary scene-setting**: Focus on elements that affect conversation. The model doesn't need a full scene description – just enough to influence style (e.g. formal office vs. casual home setting).

### 3. Tone

Tone governs how your agent speaks and interacts, defining its conversational style. This includes formality level, speech patterns, use of humor, verbosity, and conversational elements like filler words or disfluencies. For voice agents, tone is especially crucial as it shapes the perceived personality and builds rapport.

- **Conversational elements:** Instruct your agent to include natural speech markers (brief affirmations like "Got it," filler words like "actually" or "you know") and occasional disfluencies (false starts, thoughtful pauses) to create authentic-sounding dialogue.
- **TTS compatibility:** Direct your agent to optimize for speech synthesis by using punctuation strategically (ellipses for pauses, emphasis marks for key points) and adapting text formats for natural pronunciation: spell out email addresses ("john dot smith at company dot com"), format phone numbers with pauses ("five five five… one two three… four five six seven"), convert numbers into spoken forms ("$19.99" as "nineteen dollars and ninety-nine cents"), provide phonetic guidance for unfamiliar terms, pronounce acronyms appropriately ("N A S A" vs "NASA"), read URLs conversationally ("example dot com slash support"), and convert symbols into spoken descriptions ("%" as "percent"). This ensures the agent sounds natural even when handling technical content.
- **Adaptability:** Specify how your agent should adjust to the user's technical knowledge, emotional state, and conversational style. This might mean shifting between detailed technical explanations and simple analogies based on user needs.
- **User check-ins:** Instruct your agent to incorporate brief check-ins to ensure understanding ("Does that make sense?") and modify its approach based on feedback.

### 4. Goal

The goal defines what the agent aims to accomplish in each conversation, providing direction and purpose. Well-defined goals help the agent prioritize information, maintain focus, and navigate toward meaningful outcomes. Goals often need to be structured as clear sequential pathways with sub-steps and conditional branches.

- **Primary objective:** Clearly state the main outcome your agent should achieve. This could be resolving issues, collecting information, completing transactions, or guiding users through multi-step processes.
- **Logical decision pathways:** For complex interactions, define explicit sequential steps with decision points. Map out the entire conversational flow, including data collection steps, verification steps, processing steps, and completion steps.
- **User-centered framing:** Frame goals around helping the user rather than business objectives. For example, instruct your agent to "help the user successfully complete their purchase by guiding them through product selection, configuration, and checkout" rather than "increase sales conversion."
- **Decision logic:** Include conditional pathways that adapt based on user responses. Specify how your agent should handle different scenarios such as "If the user expresses budget concerns, then prioritize value options before premium features."
- **Evaluation criteria & data collection:** Define what constitutes a successful interaction, so you know when the agent has fulfilled its purpose. Include both primary metrics (e.g., "completed booking") and secondary metrics (e.g., "collected preference data for future personalization").

### 5. Guardrails

Guardrails set boundaries ensuring interactions remain appropriate and ethical. They prevent inappropriate responses to unexpected inputs and maintain brand safety.

- Keep responses focused on relevant topics
- When uncertain, acknowledge limitations transparently rather than speculating
- Avoid presenting opinions as facts
- Respond naturally without referencing being an AI or using disclaimers
- Use normalized, spoken language without abbreviations or special characters
- Mirror the user's communication style

### 6. Tools

Tools define external capabilities the agent can access beyond conversation. Clearly specify:
- What tools are available
- When to use each tool
- How to orchestrate multiple tools
- What to do if a tool fails

## Prompt Formatting

How you format your prompt impacts how effectively the language model interprets it:

- **Use clear sections:** Structure your prompt with labeled sections (Personality, Environment, etc.) or use Markdown headings for clarity.
- **Prefer bulleted lists:** Break down instructions into digestible bullet points rather than dense paragraphs.
- **Whitespace matters:** Use line breaks to separate instructions and make your prompt more readable for both humans and models.
- **Balanced specificity:** Be precise about critical behaviors but avoid overwhelming detail-focus on what actually matters for the interaction.

## Evaluate & Iterate

Prompt engineering is inherently iterative. Implement this feedback loop to continually improve your agent:

1. **Configure evaluation criteria:** Attach concrete evaluation criteria to each agent to monitor success over time & check for regressions.
2. **Analyze failures:** Identify patterns in problematic interactions.
3. **Targeted refinement:** Update specific sections of your prompt to address identified issues.
4. **Configure data collection:** Configure the agent to summarize data from each conversation.

