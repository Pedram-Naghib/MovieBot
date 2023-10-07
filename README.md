# Movie File Manager Telegram Bot

The Movie File Manager Telegram Bot simplifies your movie and series collection management. With this bot, owners can effortlessly save and organize movie file IDs in a database. Additionally, users can conveniently access these files through the bot. Whether you want to save your favorite movies, series, or documentaries, this bot streamlines the process.

## Features

*   Register new encode for movie/series: Use the /register command to register new movies or series. Add encode file IDs to the database, ensuring easy access later.

*   Add Disc Quality Files: Use the /cd command to add disc quality files to your database. Keep track of high-quality versions of your favorite movies and series.

*   Add Extra Content: Store additional content like interviews, behind-the-scenes footage, and related materials using the /extra command. Enhance your collection with rich multimedia content.

*   Edit RSS Feeds: Stay updated with the latest movies and series by editing RSS feeds with the rss command. Receive notifications about newly added or updated content in your favorite genres.

*   Delete Entries: Remove unwanted items from your database with the del command. Keep your collection clean and well-organized.

## Getting Started

1. Clone the Repository:

```bash
git clone https://github.com/yourusername/movie-file-manager-bot.git
```

2. Install Dependencies:

```pip install -r requirements.txt```

3. Configure the Bot:

*   Create a Telegram bot using the BotFather on Telegram.
*   Configure your Telegram Bot Token in the config.py file.

Run the Bot:

```python main.py```

5. Commands:
*   /register: Register new movies or series and add encode file IDs to the database.
*   /cd: Add disc quality files to the database.
*   /extra: Add additional content related to series/movies to the database.
*   rss: Edit RSS feeds for the latest movie and series updates.
*   del: Delete entries from the database.

## Contributing

Contributions are welcome! Fork the repository, make your changes, and submit a pull request. If you encounter any issues or have suggestions, please open an issue.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.