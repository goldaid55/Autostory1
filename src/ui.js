import inquirer from 'inquirer';
import chalk from 'chalk';
import { readFileSync, readdirSync } from 'fs';
import path from 'path';

export class UI {
  constructor(accountManager, storyManager) {
    this.accountManager = accountManager;
    this.storyManager = storyManager;
  }

  async start() {
    console.log(chalk.blue('🚀 Telegram Story Bot'));
    
    while (true) {
      const { action } = await inquirer.prompt([
        {
          type: 'list',
          name: 'action',
          message: 'Выберите действие:',
          choices: [
            { name: '📱 Управление аккаунтами', value: 'accounts' },
            { name: '📸 Опубликовать историю', value: 'story' },
            { name: '📅 Отложенная публикация', value: 'scheduled' },
            { name: '👥 Управление списком упоминаний', value: 'mentions' },
            { name: '🔄 Управление прокси', value: 'proxy' },
            { name: '❌ Выход', value: 'exit' }
          ]
        }
      ]);

      if (action === 'exit') break;

      switch (action) {
        case 'accounts':
          await this.accountsMenu();
          break;
        case 'story':
          await this.storyMenu();
          break;
        case 'scheduled':
          await this.scheduledMenu();
          break;
        case 'mentions':
          await this.mentionsMenu();
          break;
        case 'proxy':
          await this.proxyMenu();
          break;
      }
    }
  }

  async accountsMenu() {
    const { action } = await inquirer.prompt([
      {
        type: 'list',
        name: 'action',
        message: 'Управление аккаунтами:',
        choices: [
          { name: '➕ Добавить аккаунт', value: 'add' },
          { name: '📋 Список аккаунтов', value: 'list' },
          { name: '🔙 Назад', value: 'back' }
        ]
      }
    ]);

    if (action === 'back') return;

    if (action === 'add') {
      const { phone } = await inquirer.prompt([
        {
          type: 'input',
          name: 'phone',
          message: 'Введите номер телефона (в международном формате):',
          validate: input => input.length > 0
        }
      ]);

      try {
        await this.accountManager.addAccount(phone, process.env.API_ID, process.env.API_HASH);
        console.log(chalk.green('✅ Аккаунт успешно добавлен!'));
      } catch (err) {
        console.error(chalk.red('❌ Ошибка при добавлении аккаунта:', err.message));
      }
    }

    if (action === 'list') {
      const accounts = this.accountManager.getAccounts();
      if (accounts.length === 0) {
        console.log(chalk.yellow('ℹ️ Нет добавленных аккаунтов'));
      } else {
        console.log(chalk.blue('\nСписок аккаунтов:'));
        accounts.forEach((acc, i) => {
          console.log(chalk.white(`${i + 1}. ${acc.phone}`));
        });
      }
    }
  }

  async storyMenu() {
    const accounts = this.accountManager.getAccounts();
    if (accounts.length === 0) {
      console.log(chalk.red('❌ Сначала добавьте аккаунт!'));
      return;
    }

    const { account, mediaPath, caption, mentionsFile, link, privacy } = await inquirer.prompt([
      {
        type: 'list',
        name: 'account',
        message: 'Выберите аккаунт:',
        choices: accounts.map(acc => ({ name: acc.phone, value: acc }))
      },
      {
        type: 'input',
        name: 'mediaPath',
        message: 'Путь к медиафайлу:'
      },
      {
        type: 'input',
        name: 'caption',
        message: 'Подпись (опционально):'
      },
      {
        type: 'input',
        name: 'mentionsFile',
        message: 'Путь к файлу с упоминаниями (опционально):'
      },
      {
        type: 'input',
        name: 'link',
        message: 'Ссылка (опционально):'
      },
      {
        type: 'list',
        name: 'privacy',
        message: 'Кто может видеть историю:',
        choices: [
          { name: 'Все', value: 'all' },
          { name: 'Контакты', value: 'contacts' },
          { name: 'Близкие друзья', value: 'close_friends' },
          { name: 'Выбранные пользователи', value: 'selected' }
        ]
      }
    ]);

    try {
      const mentions = mentionsFile ? 
        await this.storyManager.loadMentionsList(mentionsFile) : [];

      await this.storyManager.postStory({
        account,
        mediaPath,
        caption,
        mentions,
        link,
        privacy
      });
      console.log(chalk.green('✅ История успешно опубликована!'));
    } catch (err) {
      console.error(chalk.red('❌ Ошибка при публикации:', err.message));
    }
  }

  async scheduledMenu() {
    const accounts = this.accountManager.getAccounts();
    if (accounts.length === 0) {
      console.log(chalk.red('❌ Сначала добавьте аккаунт!'));
      return;
    }

    const { account, mediaFolder, interval, startTime, privacy, caption, mentionsFile, link } = await inquirer.prompt([
      {
        type: 'list',
        name: 'account',
        message: 'Выберите аккаунт:',
        choices: accounts.map(acc => ({ name: acc.phone, value: acc }))
      },
      {
        type: 'input',
        name: 'mediaFolder',
        message: 'Путь к папке с медиафайлами:',
        validate: input => input.length > 0
      },
      {
        type: 'number',
        name: 'interval',
        message: 'Интервал между публикациями (в минутах):',
        default: 5,
        validate: input => input > 0
      },
      {
        type: 'input',
        name: 'startTime',
        message: 'Время начала публикаций (HH:MM):',
        default: new Date().toTimeString().slice(0, 5),
        validate: input => /^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$/.test(input)
      },
      {
        type: 'list',
        name: 'privacy',
        message: 'Кто может видеть истории:',
        choices: [
          { name: 'Все', value: 'all' },
          { name: 'Контакты', value: 'contacts' },
          { name: 'Близкие друзья', value: 'close_friends' },
          { name: 'Выбранные пользователи', value: 'selected' }
        ]
      },
      {
        type: 'input',
        name: 'caption',
        message: 'Подпись для всех историй (опционально):'
      },
      {
        type: 'input',
        name: 'mentionsFile',
        message: 'Путь к файлу с упоминаниями (опционально):'
      },
      {
        type: 'input',
        name: 'link',
        message: 'Ссылка (опционально):'
      }
    ]);

    try {
      // Получаем список медиафайлов
      const files = readdirSync(mediaFolder)
        .filter(file => {
          const ext = path.extname(file).toLowerCase();
          return ['.jpg', '.jpeg', '.png', '.mp4'].includes(ext);
        })
        .map(file => path.join(mediaFolder, file));

      if (files.length === 0) {
        console.log(chalk.yellow('⚠️ В указанной папке нет подходящих медиафайлов'));
        return;
      }

      // Загружаем список упоминаний
      const mentions = mentionsFile ? 
        await this.storyManager.loadMentionsList(mentionsFile) : [];

      // Рассчитываем время публикации для каждого файла
      const [hours, minutes] = startTime.split(':').map(Number);
      const startDate = new Date();
      startDate.setHours(hours, minutes, 0, 0);
      
      if (startDate < new Date()) {
        startDate.setDate(startDate.getDate() + 1);
      }

      console.log(chalk.blue('\n📅 Запланированные публикации:'));
      
      for (let i = 0; i < files.length; i++) {
        const publishDate = new Date(startDate.getTime() + i * interval * 60000);
        const delay = (publishDate.getTime() - Date.now()) / 1000;

        console.log(chalk.white(
          `${i + 1}. ${path.basename(files[i])} - ${publishDate.toLocaleString()}`
        ));

        // Планируем публикацию
        setTimeout(() => {
          this.storyManager.postStory({
            account,
            mediaPath: files[i],
            caption,
            mentions,
            link,
            privacy
          }).catch(err => {
            console.error(chalk.red(`❌ Ошибка при публикации ${files[i]}:`, err.message));
          });
        }, delay * 1000);
      }

      console.log(chalk.green(`\n✅ Запланировано ${files.length} публикаций`));
      
    } catch (err) {
      console.error(chalk.red('❌ Ошибка при планировании:', err.message));
    }
  }

  async mentionsMenu() {
    const { action } = await inquirer.prompt([
      {
        type: 'list',
        name: 'action',
        message: 'Управление списком упоминаний:',
        choices: [
          { name: '📝 Создать новый список', value: 'create' },
          { name: '📋 Просмотреть существующие', value: 'view' },
          { name: '🔙 Назад', value: 'back' }
        ]
      }
    ]);

    if (action === 'back') return;

    if (action === 'create') {
      const { filename } = await inquirer.prompt([
        {
          type: 'input',
          name: 'filename',
          message: 'Имя файла для сохранения:',
          default: 'mentions.txt'
        }
      ]);

      console.log(chalk.blue('Введите @username каждого пользователя с новой строки.'));
      console.log(chalk.blue('Для завершения введите пустую строку.'));

      const mentions = [];
      while (true) {
        const { username } = await inquirer.prompt([
          {
            type: 'input',
            name: 'username',
            message: 'Username:'
          }
        ]);

        if (!username) break;
        mentions.push(username);
      }

      try {
        const content = mentions.join('\n');
        writeFileSync(filename, content);
        console.log(chalk.green('✅ Список упоминаний сохранен!'));
      } catch (err) {
        console.error(chalk.red('❌ Ошибка при сохранении:', err.message));
      }
    }

    if (action === 'view') {
      const files = readdirSync('.')
        .filter(file => file.endsWith('.txt'));

      if (files.length === 0) {
        console.log(chalk.yellow('ℹ️ Нет сохраненных списков'));
        return;
      }

      const { file } = await inquirer.prompt([
        {
          type: 'list',
          name: 'file',
          message: 'Выберите файл:',
          choices: files
        }
      ]);

      try {
        const content = readFileSync(file, 'utf8');
        console.log(chalk.blue('\nСписок упоминаний:'));
        console.log(content);
      } catch (err) {
        console.error(chalk.red('❌ Ошибка при чтении файла:', err.message));
      }
    }
  }

  async proxyMenu() {
    const { action } = await inquirer.prompt([
      {
        type: 'list',
        name: 'action',
        message: 'Управление прокси:',
        choices: [
          { name: '➕ Добавить прокси', value: 'add' },
          { name: '📋 Список прокси', value: 'list' },
          { name: '🔙 Назад', value: 'back' }
        ]
      }
    ]);

    if (action === 'back') return;

    if (action === 'add') {
      const { type, host, port, username, password } = await inquirer.prompt([
        {
          type: 'list',
          name: 'type',
          message: 'Тип прокси:',
          choices: [
            { name: 'SOCKS5', value: 'socks5' },
            { name: 'HTTP', value: 'http' },
            { name: 'HTTPS', value: 'https' }
          ]
        },
        {
          type: 'input',
          name: 'host',
          message: 'Хост:',
          validate: input => input.length > 0
        },
        {
          type: 'number',
          name: 'port',
          message: 'Порт:',
          validate: input => input > 0 && input < 65536
        },
        {
          type: 'input',
          name: 'username',
          message: 'Имя пользователя (опционально):'
        },
        {
          type: 'password',
          name: 'password',
          message: 'Пароль (опционально):'
        }
      ]);

      try {
        this.accountManager.addProxy({ type, host, port, username, password });
        console.log(chalk.green('✅ Прокси успешно добавлен!'));
      } catch (err) {
        console.error(chalk.red('❌ Ошибка при добавлении прокси:', err.message));
      }
    }

    if (action === 'list') {
      const proxies = this.accountManager.getProxies();
      if (proxies.length === 0) {
        console.log(chalk.yellow('ℹ️ Нет добавленных прокси'));
      } else {
        console.log(chalk.blue('\nСписок прокси:'));
        proxies.forEach((proxy, i) => {
          console.log(chalk.white(
            `${i + 1}. ${proxy.type}://${proxy.host}:${proxy.port}`
          ));
        });
      }
    }
  }
}