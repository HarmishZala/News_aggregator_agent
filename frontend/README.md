# Briefly - News Aggregator Frontend

A clean, minimalist frontend for the Briefly news aggregator platform, built with HTML, CSS, and JavaScript.

## Features

### 🎨 Design
- **Clean, minimalist interface** matching the Figma design
- **Responsive design** that works on desktop, tablet, and mobile
- **Modern typography** using Playfair Display for headings and Inter for body text
- **Smooth animations** and transitions for better user experience

### 🔧 Functionality
- **Interactive search bar** with real-time input handling
- **Speech recognition** support for voice input
- **Microphone controls** with visual feedback
- **Keyboard shortcuts** (Ctrl/Cmd + K to focus search, Escape to clear)
- **Notification system** for user feedback
- **Responsive navigation** that adapts to different screen sizes

### 📱 Responsive Features
- **Mobile-first approach** with breakpoints at 768px and 480px
- **Collapsible navigation** on mobile devices
- **Touch-friendly buttons** and interactive elements
- **Optimized typography** scaling for different screen sizes

## File Structure

```
frontend/
├── index.html          # Main HTML structure
├── styles.css          # All styling and responsive design
├── script.js           # Interactive functionality and event handling
└── README.md           # This documentation file
```

## Getting Started

1. **Open the website**: Simply open `index.html` in your web browser
2. **Local development**: For best experience, serve the files through a local server:
   ```bash
   # Using Python
   python -m http.server 8000
   
   # Using Node.js (if you have http-server installed)
   npx http-server
   
   # Using PHP
   php -S localhost:8000
   ```

## Key Components

### Header
- **User avatar** (top-left)
- **Navigation menu** with links to Products, Solutions, Community, etc.
- **Authentication buttons** (Sign in, Register)

### Main Content
- **"Briefly" title** in elegant serif font
- **Tagline**: "No bullsh*t. Just news."
- **Search input** with interactive controls:
  - Clear button (X)
  - Microphone button (with mute/unmute)
  - Record button (for speech input)

### Footer
- **Logo** with interconnected circular shapes
- **Social media icons** (X/Twitter, Instagram, YouTube, LinkedIn)
- **Three-column link structure**:
  - Use cases
  - Explore
  - Resources

## Interactive Features

### Search Functionality
- **Real-time input handling** with debounced search simulation
- **Enter key** to trigger search
- **Loading states** with visual feedback
- **Clear functionality** with X button

### Speech Recognition
- **Voice input** support (where available)
- **Visual feedback** for recording state
- **Microphone controls** with mute/unmute functionality

### Keyboard Shortcuts
- **Ctrl/Cmd + K**: Focus on search input
- **Escape**: Clear search input
- **Enter**: Trigger search

### Notifications
- **Toast notifications** for user feedback
- **Different types**: info, success, warning, error
- **Auto-dismiss** after 3 seconds
- **Smooth animations**

## Browser Compatibility

- **Modern browsers**: Chrome, Firefox, Safari, Edge
- **Speech recognition**: Chrome, Edge (WebKit Speech API)
- **Responsive design**: All modern browsers with CSS Grid and Flexbox support

## Customization

### Colors
The design uses a monochromatic color scheme:
- **Primary**: #4a4a4a (dark gray)
- **Background**: #ffffff (white)
- **Secondary**: #f5f5f5 (light gray)
- **Text**: #000000 (black) and #666666 (medium gray)

### Typography
- **Headings**: Playfair Display (serif)
- **Body text**: Inter (sans-serif)
- **Font weights**: 300, 400, 500, 600, 700

### Breakpoints
- **Desktop**: 1200px+ (full layout)
- **Tablet**: 768px - 1199px (adjusted navigation)
- **Mobile**: 480px - 767px (stacked layout)
- **Small mobile**: < 480px (compact layout)

## Integration with Backend

The frontend is designed to easily integrate with your news aggregation backend:

1. **Search API**: Replace the `simulateSearch()` function with real API calls
2. **Authentication**: Connect the Sign in/Register buttons to your auth system
3. **Navigation**: Link the navigation items to actual pages/sections
4. **Footer links**: Connect to real content pages

## Future Enhancements

The codebase is structured to easily add:
- **News article display** components
- **User dashboard** and profile management
- **Real-time notifications** system
- **Dark mode** toggle
- **Advanced search filters**
- **Bookmarking** and favorites
- **Social sharing** functionality

## Performance

- **Lightweight**: No external dependencies except Google Fonts
- **Fast loading**: Optimized CSS and JavaScript
- **Smooth animations**: Hardware-accelerated transitions
- **Efficient event handling**: Debounced search and resize events

## Accessibility

- **Keyboard navigation** support
- **Focus indicators** for all interactive elements
- **Semantic HTML** structure
- **ARIA labels** where appropriate
- **High contrast** color scheme

## Development Notes

- **Modular JavaScript**: Functions are organized by functionality
- **CSS organization**: Styles are grouped by component
- **Event delegation**: Efficient event handling
- **Error handling**: Graceful fallbacks for unsupported features
- **Console logging**: Helpful debugging information

## License

This frontend is part of the Briefly news aggregator project.
