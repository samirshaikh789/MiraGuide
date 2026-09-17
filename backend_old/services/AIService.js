const DEMO_NOTICE = 'This is a simulated result for the AccessAI demo; please verify important details independently.';

export class AIService {
  constructor() {
    this.demoMode = process.env.DEMO_MODE !== 'false' || !process.env.AI_API_KEY;
  }

  async analyzeImage(file) {
    if (!file) throw new Error('An image is needed.');
    return {
      description: 'I can see a well-lit indoor walkway. There appears to be a door on the left and a staircase farther ahead on the right. I cannot verify distances, labels, or obstacles from this demo result.',
      confidence: 'demo',
      notice: DEMO_NOTICE,
    };
  }

  async extractText(file) {
    if (!file) throw new Error('An image is needed.');
    return 'The library will remain closed on Sunday due to maintenance. We apologise for any inconvenience.';
  }

  async transcribe(file) {
    if (!file) throw new Error('An audio recording is needed.');
    return 'Welcome to today’s accessibility workshop.';
  }

  async simplify(text, level = 'simple') {
    if (!text?.trim()) throw new Error('Text is needed.');
    const clean = text.trim();
    const prefix = level === 'child' ? 'In simple words: ' : level === 'very-simple' ? 'Very simply: ' : 'Simplified: ';
    const result = clean.length > 190
      ? `${prefix}${clean.slice(0, 175).replace(/\b(contingent upon|implementation|proposed)\b/gi, 'depending on').trim()}…`
      : `${prefix}${clean.replace(/\b(contingent upon\b)/gi, 'dependent on').replace(/\bimplementation\b/gi, 'making it happen').replace(/\butilize\b/gi, 'use')}`;
    return { text: result, notice: DEMO_NOTICE };
  }

  async summarize(text) {
    if (!text?.trim()) throw new Error('Text is needed.');
    const first = text.trim().split(/(?<=[.!?])\s+/)[0];
    return { summary: first || text.trim(), points: ['Read the key information first.', 'Ask for help if any detail is unclear.'], notice: DEMO_NOTICE };
  }

  async communicate(message) {
    if (!message?.trim()) throw new Error('A message is needed.');
    const lower = message.toLowerCase();
    if (lower.includes('pain') && lower.includes('stomach')) return 'I have pain in my stomach. Could you please help me explain this to a healthcare professional?';
    return `Could you please help me with this: ${message.trim()}?`;
  }

  async chat(message) {
    const lower = (message || '').toLowerCase();
    if (lower.includes('sign') || lower.includes('read')) return 'Try Read Text to extract words from a sign or document. Vision Assistant can also describe the surroundings around it.';
    if (lower.includes('hear') || lower.includes('caption')) return 'Open Live Captions to turn nearby speech into large, readable text.';
    if (lower.includes('speak') || lower.includes('talk')) return 'Use Communicate for large quick phrases or Voice Assistant to speak a question.';
    if (lower.includes('help') || lower.includes('emergency')) return 'If you are in immediate danger, contact local emergency services. In AccessAI, the Emergency screen can prepare a message after you confirm.';
    return 'I can help you read text, understand images, follow conversations, communicate needs, or make difficult information easier to understand. Which would you like to try?';
  }
}
