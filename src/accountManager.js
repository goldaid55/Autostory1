import { TelegramClient } from 'telegram';
import { StringSession } from 'telegram/sessions/index.js';
import fs from 'fs';

export class AccountManager {
  constructor() {
    this.accounts = [];
    this.proxies = [];
    this.loadData();
  }

  loadData() {
    try {
      if (fs.existsSync('./data/accounts.json')) {
        this.accounts = JSON.parse(fs.readFileSync('./data/accounts.json', 'utf8'));
      }
      if (fs.existsSync('./data/proxies.json')) {
        this.proxies = JSON.parse(fs.readFileSync('./data/proxies.json', 'utf8'));
      }
    } catch (err) {
      console.error('Ошибка при загрузке данных:', err);
    }
  }

  saveData() {
    try {
      if (!fs.existsSync('./data')) {
        fs.mkdirSync('./data');
      }
      fs.writeFileSync('./data/accounts.json', JSON.stringify(this.accounts, null, 2));
      fs.writeFileSync('./data/proxies.json', JSON.stringify(this.proxies, null, 2));
    } catch (err) {
      console.error('Ошибка при сохранении данных:', err);
    }
  }

  async addAccount(phone, apiId, apiHash) {
    const session = new StringSession('');
    const client = new TelegramClient(session, apiId, apiHash, {
      connectionRetries: 5
    });

    await client.start({
      phoneNumber: phone,
      password: async () => await this.promptPassword(),
      phoneCode: async () => await this.promptCode(),
      onError: err => console.log(err),
    });

    const sessionString = client.session.save();
    this.accounts.push({ phone, apiId, apiHash, session: sessionString });
    this.saveData();
    
    return client;
  }

  async promptPassword() {
    const { password } = await inquirer.prompt([
      {
        type: 'password',
        name: 'password',
        message: 'Введите пароль двухфакторной аутентификации:'
      }
    ]);
    return password;
  }

  async promptCode() {
    const { code } = await inquirer.prompt([
      {
        type: 'input',
        name: 'code',
        message: 'Введите код подтверждения:'
      }
    ]);
    return code;
  }

  getAccounts() {
    return this.accounts;
  }

  addProxy(proxy) {
    this.proxies.push(proxy);
    this.saveData();
  }

  getProxies() {
    return this.proxies;
  }
}