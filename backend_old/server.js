import 'dotenv/config';
import cors from 'cors';
import express from 'express';
import multer from 'multer';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { AIService } from './services/AIService.js';

const app = express();
const backendDirectory = path.dirname(fileURLToPath(import.meta.url));
const frontendDirectory = path.resolve(backendDirectory, '../frontend/dist');
const upload = multer({ storage: multer.memoryStorage(), limits: { fileSize: 8 * 1024 * 1024 } });
const ai = new AIService();

app.use(cors());
app.use(express.json({ limit: '1mb' }));
app.get('/api/health', (_req, res) => res.json({ success: true, demoMode: ai.demoMode }));
app.post('/api/ai/chat', async (req, res, next) => {
  try { res.json({ success: true, demoMode: ai.demoMode, reply: await ai.chat(req.body.message) }); } catch (error) { next(error); }
});
app.post('/api/ai/analyze-image', upload.single('image'), async (req, res, next) => {
  try { res.json({ success: true, demoMode: ai.demoMode, ...await ai.analyzeImage(req.file) }); } catch (error) { next(error); }
});
app.post('/api/ocr', upload.single('image'), async (req, res, next) => {
  try { res.json({ success: true, demoMode: ai.demoMode, text: await ai.extractText(req.file) }); } catch (error) { next(error); }
});
app.post('/api/transcribe', upload.single('audio'), async (req, res, next) => {
  try { res.json({ success: true, demoMode: ai.demoMode, text: await ai.transcribe(req.file) }); } catch (error) { next(error); }
});
app.post('/api/ai/simplify-text', async (req, res, next) => {
  try { res.json({ success: true, demoMode: ai.demoMode, ...await ai.simplify(req.body.text, req.body.level) }); } catch (error) { next(error); }
});
app.post('/api/summarize', async (req, res, next) => {
  try { res.json({ success: true, demoMode: ai.demoMode, ...await ai.summarize(req.body.text) }); } catch (error) { next(error); }
});
app.post('/api/ai/communicate', async (req, res, next) => {
  try { res.json({ success: true, demoMode: ai.demoMode, message: await ai.communicate(req.body.message) }); } catch (error) { next(error); }
});
app.use((error, _req, res, _next) => {
  const status = error?.code === 'LIMIT_FILE_SIZE' ? 413 : 400;
  res.status(status).json({ success: false, error: status === 413 ? 'Please choose an image under 8 MB.' : 'We could not complete that request. Please try again.' });
});
app.use(express.static(frontendDirectory));
app.get('*', (_req, res) => res.sendFile(path.join(frontendDirectory, 'index.html')));

const port = Number(process.env.PORT || 8787);
app.listen(port, () => console.log(`AccessAI API listening on http://localhost:${port} (${ai.demoMode ? 'demo mode' : 'AI mode'})`));
