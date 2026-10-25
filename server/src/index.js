import 'dotenv/config';
import express from 'express';
import cors from 'cors';
import mongoose from 'mongoose';
import path from 'node:path';

const app = express();
const port = Number(process.env.PORT || 5000);
app.use(cors());
app.use(express.json({ limit: '32kb' }));

const equipmentSchema = new mongoose.Schema({
  name: { type: String, required: true, trim: true },
  category: { type: String, required: true, trim: true },
  tag: { type: String, required: true, unique: true, trim: true },
  status: { type: String, enum: ['Available', 'On loan', 'Maintenance'], default: 'Available' },
  location: { type: String, default: 'Main Lab' }
}, { timestamps: true });
const requestSchema = new mongoose.Schema({
  student: { type: String, required: true, trim: true },
  equipment: { type: String, required: true, trim: true },
  purpose: { type: String, required: true, trim: true },
  dueDate: { type: String, required: true },
  status: { type: String, enum: ['Pending', 'Approved', 'Returned', 'Rejected'], default: 'Pending' }
}, { timestamps: true });
const Equipment = mongoose.models.Equipment || mongoose.model('Equipment', equipmentSchema);
const LoanRequest = mongoose.models.LoanRequest || mongoose.model('LoanRequest', requestSchema);

let demoEquipment = [
  { _id: 'eq-1', name: 'Digital Oscilloscope', category: 'Electronics', tag: 'EL-204', status: 'Available', location: 'Bench 04' },
  { _id: 'eq-2', name: 'Arduino Starter Kit', category: 'Prototyping', tag: 'PR-118', status: 'On loan', location: 'Cabinet B' },
  { _id: 'eq-3', name: 'Digital Multimeter', category: 'Electronics', tag: 'EL-087', status: 'Available', location: 'Bench 02' },
  { _id: 'eq-4', name: 'Soldering Station', category: 'Prototyping', tag: 'PR-032', status: 'Maintenance', location: 'Service desk' },
  { _id: 'eq-5', name: 'Bench Power Supply', category: 'Electronics', tag: 'EL-143', status: 'Available', location: 'Bench 07' },
  { _id: 'eq-6', name: 'Raspberry Pi 5 Kit', category: 'Computing', tag: 'CO-061', status: 'Available', location: 'Cabinet A' }
];
let demoRequests = [
  { _id: 'rq-1', student: 'Ananya Menon', equipment: 'Arduino Starter Kit', purpose: 'Sensor calibration lab', dueDate: '2026-10-29', status: 'Pending' },
  { _id: 'rq-2', student: 'Rohan Das', equipment: 'Digital Multimeter', purpose: 'Circuit analysis assignment', dueDate: '2026-10-28', status: 'Approved' },
  { _id: 'rq-3', student: 'Meera Nair', equipment: 'Digital Oscilloscope', purpose: 'Signal measurement practical', dueDate: '2026-10-26', status: 'Returned' }
];

const useDb = () => mongoose.connection.readyState === 1;
app.get('/api/health', (_req, res) => res.json({ ok: true, database: useDb() ? 'connected' : 'demo-memory' }));
app.get('/api/equipment', async (_req, res, next) => {
  try { res.json(useDb() ? await Equipment.find().sort({ name: 1 }).lean() : demoEquipment); } catch (err) { next(err); }
});
app.post('/api/equipment', async (req, res, next) => {
  try {
    const { name, category, tag, location = 'Main Lab' } = req.body || {};
    if (![name, category, tag].every(v => typeof v === 'string' && v.trim())) return res.status(400).json({ message: 'Name, category and asset tag are required.' });
    const item = { name: name.trim(), category: category.trim(), tag: tag.trim(), location: String(location).trim(), status: 'Available' };
    const saved = useDb() ? await Equipment.create(item) : { _id: `eq-${Date.now()}`, ...item };
    if (!useDb()) demoEquipment = [saved, ...demoEquipment];
    res.status(201).json(saved);
  } catch (err) { next(err); }
});
app.get('/api/requests', async (_req, res, next) => {
  try { res.json(useDb() ? await LoanRequest.find().sort({ createdAt: -1 }).lean() : demoRequests); } catch (err) { next(err); }
});
app.post('/api/requests', async (req, res, next) => {
  try {
    const { student, equipment, purpose, dueDate } = req.body || {};
    if (![student, equipment, purpose, dueDate].every(v => typeof v === 'string' && v.trim())) return res.status(400).json({ message: 'Complete each request field before submitting.' });
    const row = { student: student.trim(), equipment: equipment.trim(), purpose: purpose.trim(), dueDate, status: 'Pending' };
    const saved = useDb() ? await LoanRequest.create(row) : { _id: `rq-${Date.now()}`, ...row };
    if (!useDb()) demoRequests = [saved, ...demoRequests];
    res.status(201).json(saved);
  } catch (err) { next(err); }
});
app.patch('/api/requests/:id/status', async (req, res, next) => {
  try {
    const { status } = req.body || {};
    if (!['Approved', 'Returned', 'Rejected'].includes(status)) return res.status(400).json({ message: 'Choose an allowed request status.' });
    if (useDb()) {
      const saved = await LoanRequest.findByIdAndUpdate(req.params.id, { status }, { new: true, runValidators: true });
      if (!saved) return res.status(404).json({ message: 'Request not found.' });
      return res.json(saved);
    }
    const row = demoRequests.find(item => item._id === req.params.id);
    if (!row) return res.status(404).json({ message: 'Request not found.' });
    row.status = status;
    res.json(row);
  } catch (err) { next(err); }
});
app.use(express.static(path.resolve(process.cwd(), 'client/dist')));
app.use((req, res, next) => {
  if (req.method !== 'GET' || req.path.startsWith('/api/')) return next();
  res.sendFile(path.resolve(process.cwd(), 'client/dist/index.html'), err => { if (err) next(); });
});
app.use((err, _req, res, _next) => {
  console.error(err.message);
  res.status(500).json({ message: 'The request could not be completed.' });
});

if (process.env.MONGODB_URI) {
  mongoose.connect(process.env.MONGODB_URI).then(() => console.log('MongoDB connected')).catch(err => console.error('MongoDB connection failed:', err.message));
} else {
  console.log('No MONGODB_URI supplied; using in-memory demo records.');
}
app.listen(port, '0.0.0.0', () => console.log(`LabDesk API listening on ${port}`));
