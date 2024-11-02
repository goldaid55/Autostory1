import { config } from 'dotenv';
import { UI } from './ui.js';
import { AccountManager } from './accountManager.js';
import { StoryManager } from './storyManager.js';

config();

async function main() {
  const accountManager = new AccountManager();
  const storyManager = new StoryManager();
  const ui = new UI(accountManager, storyManager);
  
  await ui.start();
}

main().catch(console.error);