window.addEventListener('DOMContentLoaded', () => {
  const input = document.getElementById('prompt-input');
  const btn = document.getElementById('generate-btn');
  const cards = document.getElementById('cards');

  async function handle() {
    const prompt = input.value.trim();
    if (!prompt) return;
    cards.innerHTML = '生成中...';
    const ideas = await window.electronAPI.generateIdeas(prompt);
    if (!ideas || ideas.error) {
      cards.innerHTML = `<p class="error">${ideas.error || '生成失败'}</p>`;
      return;
    }
    cards.innerHTML = '';
    ideas.forEach((idea) => {
      const div = document.createElement('div');
      div.className = 'card';
      div.textContent = idea;
      cards.appendChild(div);
    });
  }

  btn.addEventListener('click', handle);
});
