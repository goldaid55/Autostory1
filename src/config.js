import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';

dotenv.config();

const __dirname = path.dirname(fileURLToPath(import.meta.url));

export const config = {
  apiId: process.env.API_ID,
  apiHash: process.env.API_HASH,
  sessionPath: process.env.SESSION_PATH || path.join(__dirname, '../sessions'),
  dataPath: path.join(__dirname, '../data')
};