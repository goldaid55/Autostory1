import fs from 'fs';
import path from 'path';

export function ensureDirectoryExists(dirPath) {
  if (!fs.existsSync(dirPath)) {
    fs.mkdirSync(dirPath, { recursive: true });
  }
}

export function isImageFile(filePath) {
  const ext = path.extname(filePath).toLowerCase();
  return ['.jpg', '.jpeg', '.png'].includes(ext);
}

export function isVideoFile(filePath) {
  const ext = path.extname(filePath).toLowerCase();
  return ['.mp4', '.mov'].includes(ext);
}

export function validateMediaFile(filePath) {
  if (!fs.existsSync(filePath)) {
    throw new Error('Файл не найден');
  }
  
  if (!isImageFile(filePath) && !isVideoFile(filePath)) {
    throw new Error('Неподдерживаемый формат файла');
  }
  
  const stats = fs.statSync(filePath);
  const fileSizeInMB = stats.size / (1024 * 1024);
  
  if (fileSizeInMB > 50) {
    throw new Error('Файл слишком большой (максимум 50MB)');
  }
}