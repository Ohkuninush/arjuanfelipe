/*
  Animated terminal:
  - types each command character by character
  - keeps the card at a fixed height, latest lines anchored to the bottom
  - runs "clear" and starts again
  Language-neutral content, shared by the EN and ES pages.
*/
const terminal = document.getElementById("terminal-screen");

if (terminal) {
  const commands = [
    { command: "whoami", output: "juan_felipe" },
    { command: "focus", output: "quality · data · engineering" },
    { command: "skills", output: "SQL · Python · Java" },
    { command: "building", output: "Kaizen · Colorimetria · WOM" },
    { command: "experience", output: "QA · Data · BI · Automation" },
    { command: "status", output: "building_" }
  ];

  const prompt = "user@arjuanfelipe:~$";
  const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));

  const typeInto = async (element, text, speed = 34) => {
    for (const char of text) {
      element.textContent += char;
      await sleep(speed);
    }
  };

  const showCommand = async item => {
    const commandLine = document.createElement("div");
    commandLine.className = "terminal-line";

    const promptSpan = document.createElement("span");
    promptSpan.className = "prompt";
    promptSpan.textContent = prompt + " ";

    const commandSpan = document.createElement("span");
    commandSpan.className = "command";

    commandLine.appendChild(promptSpan);
    commandLine.appendChild(commandSpan);
    terminal.appendChild(commandLine);

    await typeInto(commandSpan, item.command, 68);
    await sleep(520);

    const outputLine = document.createElement("div");
    outputLine.className = "terminal-line output";
    outputLine.textContent = item.output;
    terminal.appendChild(outputLine);

    await sleep(1100);
  };

  const terminalLoop = async () => {
    while (true) {
      terminal.innerHTML = "";

      for (const item of commands) {
        await showCommand(item);
      }

      const clearLine = document.createElement("div");
      clearLine.className = "terminal-line terminal-clear";
      clearLine.textContent = prompt + " clear";
      terminal.appendChild(clearLine);

      await sleep(250);
      clearLine.classList.add("visible");
      await sleep(600);

      terminal.innerHTML = "";
      await sleep(450);
    }
  };

  terminalLoop();
}
