"""
Symbol Representation for Symbol Table
Represents a single symbol (variable, function, procedure, etc.) in the compiler
"""

from enum import Enum
from typing import Optional, Dict, Any


class SymbolKind(Enum):
    """Types of symbols that can be stored in the symbol table"""
    VARIABLE = "variable"
    CONSTANT = "constant"
    FUNCTION = "function"
    PROCEDURE = "procedure"
    ARRAY = "array"
    PARAMETER = "parameter"
    TYPE = "type"


class DataType(Enum):
    """Supported data types"""
    INTEGER = "integer"
    REAL = "real"
    BOOLEAN = "boolean"
    UNDEFINED = "undefined"


class Symbol:
    """
    Represents a single symbol in the symbol table.
    
    Attributes:
        name (str): Symbol name (identifier)
        kind (SymbolKind): What kind of symbol (variable, function, etc.)
        data_type (DataType): Data type of the symbol
        scope_level (int): Nesting level (0 = global)
        line_number (int): Line where declared
        column_number (int): Column where declared
        attributes (Dict): Additional attributes (array size, function params, etc.)
    """
    
    def __init__(self, name: str, kind: SymbolKind, data_type: DataType,
                 scope_level: int, line_number: int, column_number: int):
        """
        Initialize a symbol.
        
        Args:
            name: Symbol name
            kind: Symbol kind
            data_type: Data type
            scope_level: Scope nesting level
            line_number: Line where declared
            column_number: Column where declared
        """
        self.name = name
        self.kind = kind
        self.data_type = data_type
        self.scope_level = scope_level
        self.line_number = line_number
        self.column_number = column_number
        self.attributes: Dict[str, Any] = {}
    
    def set_attribute(self, key: str, value: Any) -> None:
        """
        Set an attribute on the symbol.
        
        Args:
            key: Attribute key
            value: Attribute value
        """
        self.attributes[key] = value
    
    def get_attribute(self, key: str, default: Any = None) -> Any:
        """
        Get an attribute from the symbol.
        
        Args:
            key: Attribute key
            default: Default value if not found
            
        Returns:
            Attribute value or default
        """
        return self.attributes.get(key, default)
    
    def add_parameter(self, param_name: str, param_type: DataType) -> None:
        """
        Add a parameter to a function/procedure.
        
        Args:
            param_name: Parameter name
            param_type: Parameter type
        """
        if 'parameters' not in self.attributes:
            self.attributes['parameters'] = []
        self.attributes['parameters'].append((param_name, param_type))
    
    def get_parameters(self):
        """Get list of parameters for function/procedure"""
        return self.attributes.get('parameters', [])
    
    def set_array_info(self, element_type: DataType, lower_bound: int, 
                      upper_bound: int) -> None:
        """
        Set array information.
        
        Args:
            element_type: Type of array elements
            lower_bound: Lower index bound
            upper_bound: Upper index bound
        """
        self.attributes['element_type'] = element_type
        self.attributes['lower_bound'] = lower_bound
        self.attributes['upper_bound'] = upper_bound
    
    def get_array_info(self) -> tuple:
        """Get array information"""
        return (
            self.attributes.get('element_type'),
            self.attributes.get('lower_bound'),
            self.attributes.get('upper_bound')
        )
    
    def __str__(self) -> str:
        """Return string representation"""
        attr_str = ""
        if self.attributes:
            attr_str = f", attributes={self.attributes}"
        return (f"Symbol(name={self.name}, kind={self.kind.value}, "
                f"type={self.data_type.value}, scope={self.scope_level}, "
                f"line={self.line_number}{attr_str})")
    
    def __repr__(self) -> str:
        """Return detailed string representation"""
        return self.__str__()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert symbol to dictionary"""
        return {
            'name': self.name,
            'kind': self.kind.value,
            'type': self.data_type.value,
            'scope_level': self.scope_level,
            'line_number': self.line_number,
            'column_number': self.column_number,
            'attributes': self.attributes
        }


class SymbolBuilder:
    """
    Builder class for creating symbols with fluent interface.
    """
    
    def __init__(self, name: str, kind: SymbolKind, scope_level: int,
                 line_number: int, column_number: int):
        """Initialize builder"""
        self.symbol = Symbol(name, kind, DataType.UNDEFINED, scope_level,
                            line_number, column_number)
    
    def with_type(self, data_type: DataType) -> 'SymbolBuilder':
        """Set data type"""
        self.symbol.data_type = data_type
        return self
    
    def with_attribute(self, key: str, value: Any) -> 'SymbolBuilder':
        """Add attribute"""
        self.symbol.set_attribute(key, value)
        return self
    
    def with_array(self, element_type: DataType, lower: int, upper: int) -> 'SymbolBuilder':
        """Add array information"""
        self.symbol.set_array_info(element_type, lower, upper)
        return self
    
    def with_parameter(self, param_name: str, param_type: DataType) -> 'SymbolBuilder':
        """Add parameter"""
        self.symbol.add_parameter(param_name, param_type)
        return self
    
    def build(self) -> Symbol:
        """Build and return the symbol"""
        return self.symbol


if __name__ == '__main__':
    # Example usage
    var_symbol = Symbol("x", SymbolKind.VARIABLE, DataType.INTEGER, 0, 5, 8)
    print(f"Variable: {var_symbol}")
    
    func_symbol = SymbolBuilder("gcd", SymbolKind.FUNCTION, 0, 10, 5) \
        .with_type(DataType.INTEGER) \
        .with_parameter("a", DataType.INTEGER) \
        .with_parameter("b", DataType.INTEGER) \
        .build()
    print(f"Function: {func_symbol}")
    print(f"Parameters: {func_symbol.get_parameters()}")
    
    array_symbol = SymbolBuilder("arr", SymbolKind.ARRAY, 0, 15, 5) \
        .with_array(DataType.INTEGER, 1, 100) \
        .build()
    print(f"Array: {array_symbol}")
    print(f"Array info: {array_symbol.get_array_info()}")
