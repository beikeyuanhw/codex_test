window.addEventListener('DOMContentLoaded', () => {
  const input = document.getElementById('prompt-input');
  const btn = document.getElementById('generate-btn');
  const cards = document.getElementById('cards');

  async function handle() {
    const prompt = input.value.trim();
    if (!prompt) return;
    cards.innerHTML = '生成中...';
    try {
      const ideas = await window.electronAPI.generateIdeas(prompt);
      if (!ideas || ideas.error) {
        const msg = ideas?.error?.includes('OPENAI_API_KEY')
          ? '未配置 OpenAI API 密钥'
          : ideas?.error || '生成失败';
        cards.innerHTML = `<p class="error">${msg}</p>`;
        return;
      }
      if (!ideas.length) {
        cards.innerHTML = '<p class="error">没有生成结果</p>';
        return;
      }
      cards.innerHTML = '';
      ideas.forEach((idea) => {
        const div = document.createElement('div');
        div.className = 'card';
        div.textContent = idea;
        cards.appendChild(div);
      });
    } catch (err) {
      cards.innerHTML = `<p class="error">${err}</p>`;
    }
  }

  btn.addEventListener('click', handle);
});
