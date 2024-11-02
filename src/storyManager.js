import { Api } from 'telegram';
import { readFileSync } from 'fs';
import { validateMediaFile } from './utils.js';

export class StoryManager {
  async postStory({ account, mediaPath, caption = '', mentions = [], link = '', privacy = 'all', delay = 0 }) {
    validateMediaFile(mediaPath);
    
    if (delay > 0) {
      await new Promise(resolve => setTimeout(resolve, delay * 1000));
    }

    const client = await this.getClient(account);
    
    // Проверяем возможность отправки историй
    const canSend = await client.invoke(
      new Api.stories.CanSendStory({
        peer: 'me'
      })
    );

    if (!canSend) {
      throw new Error('Невозможно отправить историю в данный момент');
    }

    // Загружаем медиафайл
    const buffer = readFileSync(mediaPath);
    const file = await client.uploadFile({
      file: buffer,
      workers: 1
    });

    // Подготавливаем медиа
    const mediaInput = new Api.InputMediaUploadedPhoto({
      file: file
    });

    // Формируем правила приватности
    const privacyRules = [];
    switch(privacy) {
      case 'all':
        privacyRules.push(new Api.InputPrivacyValueAllowAll());
        break;
      case 'contacts':
        privacyRules.push(new Api.InputPrivacyValueAllowContacts());
        break;
      case 'close_friends':
        privacyRules.push(new Api.InputPrivacyValueAllowCloseFriends());
        break;
      case 'selected':
        if (mentions.length > 0) {
          privacyRules.push(new Api.InputPrivacyValueAllowUsers({ users: mentions }));
        }
        break;
    }

    // Формируем текст с упоминаниями
    let fullCaption = caption;
    if (mentions.length > 0) {
      const mentionedUsers = await Promise.all(
        mentions.map(username => client.getEntity(username))
      );
      fullCaption += '\n' + mentionedUsers.map(user => 
        `[${user.firstName}](tg://user?id=${user.id})`
      ).join(' ');
    }
    if (link) {
      fullCaption += '\n' + link;
    }

    // Отправляем историю
    const result = await client.invoke(
      new Api.stories.SendStory({
        peer: 'me',
        media: mediaInput,
        caption: fullCaption,
        privacyRules: privacyRules,
        period: 86400, // 24 часа
        pinned: false
      })
    );

    return result;
  }

  async getClient(account) {
    const { TelegramClient } = await import('telegram');
    const { StringSession } = await import('telegram/sessions/index.js');
    
    const client = new TelegramClient(
      new StringSession(account.session),
      account.apiId,
      account.apiHash,
      {
        connectionRetries: 5
      }
    );

    await client.connect();
    return client;
  }

  async loadMentionsList(filePath) {
    try {
      const content = readFileSync(filePath, 'utf8');
      return content.split('\n').map(line => line.trim()).filter(Boolean);
    } catch (err) {
      throw new Error('Ошибка при загрузке списка упоминаний');
    }
  }
}