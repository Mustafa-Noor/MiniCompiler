"""
Double Buffering Implementation for Lexical Analysis
Implements efficient input buffering with two buffers and forward/lexemeBegin pointers
"""

class Buffer:
    """
    Implements double buffering for the lexical analyzer
    
    Uses two buffers to efficiently read source code with look-ahead capability.
    Maintains forward and lexemeBegin pointers for token recognition.
    
    Attributes:
        buffer_size (int): Size of each buffer
        source_file (str): Path to source file
        buffer1 (str): First buffer
        buffer2 (str): Second buffer
        active_buffer (int): Currently active buffer (1 or 2)
        forward (int): Position in active buffer
        lexeme_begin (int): Start of current lexeme
        eof_reached (bool): Whether end of file has been reached
        line_no (int): Current line number
        col_no (int): Current column number
    """
    
    def __init__(self, source_file, buffer_size=1024):
        """
        Initialize the double buffer
        
        Args:
            source_file (str): Path to the source code file
            buffer_size (int): Size of each buffer (default 1024)
        """
        self.buffer_size = buffer_size
        self.source_file = source_file
        self.buffer1 = ""
        self.buffer2 = ""
        self.active_buffer = 1
        self.forward = 0
        self.lexeme_begin = 0
        self.eof_reached = False
        self.line_no = 1
        self.col_no = 1
        self.file_handle = None
        
        # Open the file and load initial buffers
        try:
            self.file_handle = open(source_file, 'r', encoding='utf-8')
            self._load_buffers()
        except IOError as e:
            raise IOError(f"Cannot open source file: {source_file}\n{e}")
    
    def _load_buffers(self):
        """Load both buffers with source code"""
        self.buffer1 = self.file_handle.read(self.buffer_size)
        self.buffer2 = self.file_handle.read(self.buffer_size)
        
        if len(self.buffer1) < self.buffer_size:
            self.eof_reached = True
    
    def _reload_buffer(self, buffer_num):
        """
        Reload a buffer when it's exhausted
        
        Args:
            buffer_num (int): Buffer number to reload (1 or 2)
        """
        if buffer_num == 1:
            self.buffer1 = self.file_handle.read(self.buffer_size)
            if len(self.buffer1) < self.buffer_size:
                self.eof_reached = True
        else:
            self.buffer2 = self.file_handle.read(self.buffer_size)
            if len(self.buffer2) < self.buffer_size:
                self.eof_reached = True
    
    def get_char(self):
        """
        Get the next character and advance forward pointer
        
        Returns:
            str: Next character or '\0' if EOF
        """
        if self.eof_reached and self._is_at_end():
            return '\0'
        
        # Get current buffer and character
        if self.active_buffer == 1:
            if self.forward >= len(self.buffer1):
                # Switch to buffer2
                self.active_buffer = 2
                self.forward = 0
                if self.forward >= len(self.buffer2) and not self.eof_reached:
                    self._reload_buffer(2)
                    self.forward = 0
        else:
            if self.forward >= len(self.buffer2):
                # Switch to buffer1
                self.active_buffer = 1
                self.forward = 0
                if self.forward >= len(self.buffer1) and not self.eof_reached:
                    self._reload_buffer(1)
                    self.forward = 0
        
        # Get the current character
        current_buffer = self.buffer1 if self.active_buffer == 1 else self.buffer2
        if self.forward >= len(current_buffer):
            return '\0'
        
        char = current_buffer[self.forward]
        
        # Update line and column tracking
        if char == '\n':
            self.line_no += 1
            self.col_no = 1
        else:
            self.col_no += 1
        
        self.forward += 1
        return char
    
    def peek_char(self):
        """
        Peek at the next character without advancing
        
        Returns:
            str: Next character or '\0' if EOF
        """
        if self._is_at_end():
            return '\0'
        
        # Determine which buffer and position to peek at
        buffer_num = self.active_buffer
        pos = self.forward
        
        if buffer_num == 1:
            if pos >= len(self.buffer1):
                buffer_num = 2
                pos = 0
        else:
            if pos >= len(self.buffer2):
                buffer_num = 1
                pos = 0
        
        current_buffer = self.buffer1 if buffer_num == 1 else self.buffer2
        if pos >= len(current_buffer):
            return '\0'
        
        return current_buffer[pos]
    
    def _is_at_end(self):
        """
        Check if we're at the end of file
        
        Returns:
            bool: True if at EOF, False otherwise
        """
        if not self.eof_reached:
            return False
        
        if self.active_buffer == 1:
            return self.forward >= len(self.buffer1)
        else:
            return self.forward >= len(self.buffer2)
    
    def get_lexeme(self):
        """
        Get the current lexeme from lexeme_begin to forward
        
        Returns:
            str: The current lexeme
        """
        if self.active_buffer == 1:
            # Entire lexeme is in buffer1
            if self.lexeme_begin < len(self.buffer1):
                return self.buffer1[self.lexeme_begin:self.forward]
        else:
            # Lexeme might span buffers or be entirely in buffer2
            if self.lexeme_begin < len(self.buffer1):
                # Lexeme spans from buffer1 to buffer2
                part1 = self.buffer1[self.lexeme_begin:]
                part2 = self.buffer2[:self.forward]
                return part1 + part2
            else:
                # Entire lexeme is in buffer2
                return self.buffer2[self.lexeme_begin - len(self.buffer1):self.forward]
    
    def mark_lexeme_begin(self):
        """Mark the beginning of a lexeme"""
        self.lexeme_begin = self.forward
    
    def get_current_line(self):
        """Get current line number"""
        return self.line_no
    
    def get_current_column(self):
        """Get current column number"""
        return self.col_no
    
    def close(self):
        """Close the source file"""
        if self.file_handle:
            self.file_handle.close()
    
    def __del__(self):
        """Destructor - ensure file is closed"""
        self.close()
