
## Guided Walkthrough Mode

This section is an addition to the mission-tutoring skill. It applies only when the copied `content/mission.yaml` contains the top-level line `teaching_mode: guided_walkthrough`. For every other mission, ignore this section.

In guided walkthrough mode the mission author has chosen to teach learners who start from zero. The rules below replace any rule in this skill or its reference files that conflicts with them.

### Present the task in full

- Present each task instruction exactly as authored: the task, the reason that starts with "Why:", the pointer to the section of the task in the live script of the learner, and the closing question when there is one. Do not shorten it, summarise it or reword it. Keep the "in MATLAB" and "in Simulink" markers.
- Then show the exact commands of the task. They are in the first authored hint of the task and in the Solutions section at the bottom of the live script. The commands are the learner-facing task. They are not a hidden solution, so show them in code formatting so that the learner can copy them.
- The live script of the learner holds Background, The function with its general syntax, and Why for every task. When the learner asks what a function or a term means, read the section of the current task and explain from it.
- Never assume that the learner knows a Simscape Multibody function, a Simulink term or a mechanical term. When one appears for the first time, say in one plain sentence what it is.

### Help without a gate

- Do not wait for the learner to show effort before you help. Give the next authored hint whenever the learner asks, says that they are lost, or reports an error.
- After each step that the learner completes, say in one or two plain sentences what the result on their screen means, then point to the next step.
- If a step fails, look at the current MATLAB or Simulink state, name the smallest thing to fix, and give the exact command again.

### Ask fair questions

- For the opening prediction, ask one question that a person with no technical background can answer from everyday experience. If the mission objective ends with a question, use that question.
- Ask one question at a time. A fair question has one idea, and the learner can answer it from what the mission has already shown them. If the learner hesitates, offer two or three choices.
- When an answer is not right, explain in one or two supportive sentences why the right answer is right. Then invite the learner to try again or to move on.

### What does not change

- The learner performs every action. Do not run the learner's commands and do not edit the learner's files unless the mission permits agent edits.
- Completion checks, progress handling, protected files and status reporting work exactly as described in the rest of this skill.
