# GeneratorHub

> A modern, all-in-one generator toolbox for developers, gamers, creators, students, and everyday users.

## Features

GeneratorHub is a comprehensive suite of 10+ generators packed into a sleek, cyberpunk-inspired dark UI with smooth animations and modular architecture.

### Generator Categories

- **Developer Tools** – README Generator, JSON Generator
- **Security** – Password Generator
- **Documents** – PDF Invoice Generator
- **Creative** – Random Text Generator, Color Palette Generator
- **Utility** – QR Code Generator, File Name Generator, Fake Data Generator
- **Gaming** – Username Generator

### Core Features

- **Modern Dark UI** – Cyberpunk-inspired interface with smooth transitions
- **Sidebar Navigation** – Quick access to all generators
- **Search & Filter** – Find generators instantly
- **Favorites System** – Pin your most-used generators
- **Export History** – Track all your generated files
- **Settings** – Customize themes and notifications
- **Modular Plugin System** – Easy to extend with new generators

### Included Generators

#### 1. README Generator
- Generate professional GitHub README files
- Project name, description, features, installation, usage sections
- Technologies and license sections
- Markdown preview
- Export to README.md

#### 2. Password Generator
- Generate secure passwords with customizable options
- Adjustable length (8-64 characters)
- Toggle uppercase, lowercase, digits, symbols
- Password strength meter
- Copy to clipboard
- Password history
- Bulk generation (10+ passwords)

#### 3. QR Code Generator
- Generate QR codes from text, URLs
- Wi-Fi QR generator (SSID, password, security)
- Contact card QR generator (vCard)
- Export to PNG/SVG
- Live preview
- QR history

#### 4. PDF Invoice Generator
- Create professional PDF invoices
- Company and client information
- Add products/services with quantities and prices
- Automatic totals and tax calculations
- Export to PDF
- Invoice templates

#### 5. Username Generator
- Generate gaming usernames
- Random usernames
- Stylish usernames with special characters
- Custom prefixes/suffixes
- Username availability checker mockup
- Bulk generation (20 usernames)

#### 6. Random Text Generator
- Random bios for profiles
- Random descriptions for projects
- Random project ideas
- Random quotes
- Random gamer tags
- Customizable count (1-10)
- Export all generated text

#### 7. File Name Generator
- Batch filename generation
- Numbered filenames
- Random filenames
- Timestamp-based filenames
- UUID-based filenames
- Custom prefixes/suffixes
- Export filename lists

#### 8. Fake Data Generator
- Generate fake names
- Fake emails
- Fake phone numbers
- Fake addresses
- Complete fake profiles
- Export generated data

#### 9. Color Palette Generator
- Generate color palettes with various schemes
- Complementary, triadic, analogous, monochromatic
- RGB/HEX conversion
- Copy individual colors
- Export palettes as PNG
- Palette history

#### 10. JSON Generator
- Generate JSON templates
- User profiles, API responses, config files
- Product catalogs
- Pretty formatting
- JSON validation
- Export to JSON files

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/Copsjr57/GeneratorHub.git
   cd GeneratorHub
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python main.py
   ```

### Dependencies

GeneratorHub uses the following Python packages:

- `customtkinter==5.2.2` – Modern UI framework
- `qrcode==7.4.2` – QR code generation
- `pillow==10.4.0` – Image processing
- `pyperclip==1.9.0` – Clipboard access
- `markdown==3.6` – Markdown processing
- `reportlab==4.2.2` – PDF generation

## Usage

### Getting Started

1. Launch GeneratorHub by running `python main.py`
2. The main window opens with the home dashboard
3. Use the sidebar to navigate between generators
4. Search for specific generators using the top search bar
5. Click on any generator card to open it

### Working with Generators

Each generator follows a consistent pattern:

1. **Input** – Configure options and enter data
2. **Generate** – Click the generate button to create content
3. **Preview** – View the generated content in real-time
4. **Export** – Save to file or copy to clipboard
5. **History** – Access previous generations

### Favorites and Recent

- **Favorites** – Click the star icon on any generator to mark it as a favorite
- **Recent** – Recently used generators appear automatically in the sidebar
- **Search** – Use the search bar to quickly find generators

### Settings

Access settings from the sidebar:

- **Theme** – Choose between Dark, Light, or System theme
- **Notifications** – Enable/disable toast notifications
- **Export Location** – All exports are saved to the `exports/` folder

### Export Locations

Generated files are automatically saved to:

```
GeneratorHub/
├── exports/          # All generated files
│   ├── README.md
│   ├── qr_code.png
│   ├── invoice_001.pdf
│   └── ...
├── app/_data/        # App settings and history
└── assets/           # Icons and resources
```

## Architecture

GeneratorHub is built with a modular, plugin-based architecture:

```
GeneratorHub/
├── app/              # Main application
│   ├── app_window.py # Main window and app logic
│   └── main.py       # Entry point
├── generators/       # Generator plugins
│   ├── base.py       # Plugin interface
│   ├── registry.py   # Plugin discovery
│   └── plugins/      # Individual generators
├── ui/               # User interface
│   ├── sidebar.py    # Navigation sidebar
│   ├── topbar.py     # Search and controls
│   ├── toast.py      # Notification system
│   ├── transitions.py # Smooth animations
│   └── pages/        # Home and settings pages
├── utils/            # Utilities
│   ├── paths.py      # Path management
│   └── storage.py    # Settings and history
└── assets/           # Icons and resources
```

### Plugin System

Each generator is implemented as a separate plugin:

1. **Plugin Class** – Implements the `GeneratorPlugin` interface
2. **UI Frame** – CustomTkinter frame for the generator UI
3. **Logic** – Business logic for generation and export
4. **Registration** – Auto-discovered by the registry

### Adding New Generators

1. Create a new file in `generators/plugins/`
2. Implement the `GeneratorPlugin` interface
3. Define the generator metadata (name, category, icon, description)
4. Create the UI frame with input controls and preview
5. Implement generation and export logic
6. The generator will be auto-discovered on app startup

## Contributing

We welcome contributions! Here's how to get started:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-generator`)
3. Add your generator plugin
4. Test thoroughly
5. Commit your changes (`git commit -m 'Add amazing generator'`)
6. Push to the branch (`git push origin feature/amazing-generator`)
7. Open a Pull Request

### Guidelines

- Follow the existing code style and patterns
- Add proper error handling and validation
- Include export functionality
- Update this README if adding new features
- Test on multiple platforms if possible

## License

This project is licensed under the MIT License

## Support

- **Issues** – Report bugs or request features on GitHub Issues
- **Discussions** – Ask questions and share ideas in GitHub Discussions
- **Documentation** – Check the `docs/` folder for detailed guides

## Acknowledgments

- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) – Modern UI framework
- [qrcode](https://github.com/lincolnloop/python-qrcode) – QR code generation
- [Pillow](https://github.com/python-pillow/Pillow) – Image processing
- [ReportLab](https://www.reportlab.com/) – PDF generation
- [Markdown](https://github.com/Python-Markdown/markdown) – Markdown processing

---

**GeneratorHub** – Your all-in-one generator toolbox!
