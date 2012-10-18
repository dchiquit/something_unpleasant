OPERATIONS = {
    :binary => ['+', '-', '*', '/', '&', '|', '<', '>', '='],
    :unary => ['-', '~'],
    :all => ['+', '-', '*', '/', '&', '|', '<', '>', '=', '~', '['] #bracket operator
}

OPERATOR_MAP = {
    :binary => {
        '+' => "add",
        '-' => "sub",
        '*' => "mult",
        '/' => "divide",
        '&' => "and",
        '|' => "or",
        '<' => "lt",
        '>' => "gt",
        '=' => "eq" ###quite unfortunate
    },
    :unary => {
        '~' => "not",
        '-' => "neg"
    }
}

KEYWORDS = [
    "class",
    "constructor",
    "function",
    "method",
    "field",
    "static",
    "var",
    "int",
    "char",
    "boolean",
    "void",
    "true",
    "false",
    "null",
    "this",
    "let",
    "do",
    "if",
    "else",
    "while",
    "return"
]

SYMBOLS = ['{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', '*', '/', '&', '|', '<', '>', '=', '_'];

KEYWORD_CONSTANTS = [:this, :true, :false, :null]

class JackExpressionTree
    attr_accessor :children, :parent, :value, :type
    #@type is :operator, :function_call, :keyword_constant, or :x_terminal
    #@terminal_type is identifier, :int, :string or :char

    def initialize(parent, value, type, children = [])
        @children, @parent, @value = children, parent, value
        children.each { |child| child.parent = self }
        if (OPERATIONS[:all].include? value)
            @type = :operator
        elsif type == :function
            @type = :function_call
        elsif type == :variable
            @type = :variable
        elsif (value.is_a? String)
            @type = :string_terminal
        elsif (value.is_a? Integer)
            @type = :integer_terminal
        elsif (KEYWORD_CONSTANTS.include? value)
            @type = :keyword_constant
        ###if_statement, while_statement, let_statement, do_statement, return_statement
        ###class, variable_declaration, 
        else
            raise "Invalid tree node."
        end
    end

    def add(x)
        x.parent = self
        @children.push x
    end

    def add_subtree(value)
        @children.push(JackExpressionTree.new(self, value))
    end
end

class JackTokenizer
    def initialize(file_name)
        @file_name = file_name
        @file = File.open(file_name, "r")
        @reverse_tokens = []
        @in_comment = false
        @current_position = 0
        @relative_position = 0
        @next_line = ""
        @current_token = nil
        @current_type = nil
    end

    def find_next_token #finds token, pops from @next_line
        SYMBOLS.each { |symbol|
            @next_line.gsub! /#{"\\" + symbol}/, " #{symbol} "
        }
        @next_line.strip!
        ###the following does not check for bad strings
        tokens = @next_line.scan(/(?:"")|(?:(".*[^\\]"))|(\w+)/).flatten.compact
        #find keywords
        KEYWORDS.each { |keyword|
            if tokens.first == keyword
                @next_line.sub! /#{keyword}/, " "
                return :keyword, :"#{keyword}"
            end
        }
        #find symbols
        SYMBOLS.each { |symbol|
            if tokens.first == symbol
                @next_line.sub! /#{"\\" + symbol}/, " "
                return :symbol, symbol
            end
        }
        #find integer terminals
        if tokens.first =~ /^[\d]+$/
            @next_line.sub! /#{tokens.first}/, " "
            return :integer, tokens.first.to_i
        end
        #find string terminals
        if tokens.first.chars.first == "\""
            @next_line = @next_line[tokens.first.size..-1]
            return :string, tokens.first[1...-1].gsub(/\\/, "")
        end
        #find identifiers
        if tokens.first =~ /^[A-Za-z_]([A-Za-z0-9_]*)$/
            @next_line = @next_line[tokens.first.size..-1]
            return :identifier, tokens.first
        end
        return nil, nil
    end

    def advance
        @current_position += 1
        if @relative_position == 0
            #parse current line before moving on
            @current_type, @current_token = self.find_next_token
            while @current_token == nil
                #get new line and process
                @next_line = @file.gets
                if @in_comment and @next_line.index("*/") != nil
                    @next_line = @next_line[@next_line.index("*/")..-1]
                    @in_comment = false
                end
                @next_line.gsub! /\/\*(((?!(\*\/)).)*)\*\//, " " #removes /**/ comments
                @next_line.gsub! /\/\/(.*)$/, " " #removes // comments
                @next_line.gsub! /\/\*(.*)$/, " " #removes part of string after /*
                @next_line.gsub! /\s+/, " "
                @current_type, @current_token = self.find_next_token
            end
            @reverse_tokens.push [@current_type, @current_token]
        else
            @relative_position += 1
            @current_type, @current_token = @reverse_tokens[@current_position - 1 + @relative_position]
        end
    end

    def reverse
        @relative_position -= 1
        @current_type, @current_token = @reverse_tokens[@current_position - 1 + @relative_position]
    end

    def can_advance
        !(@next_line =~ /^([\s]*)$/ and @file.eof?)
    end

    def current_token_type
        @current_type
    end

    def get_value
        @current_token
    end
end

class JackCompiler
    def initialize(tokenizer, file_name)
        @tokenizer, @file_name = tokenizer, file_name
        @file = File.open(@file_name, "w")
        @class_name = ""
        @function_name = "___default"
        @function_mode = :default
        @static_count = 0
        @class_variable_count = 0
        @method_type = {}
        @function_variable_count = {}
        @function_argument_count = {}
        @static_resolution = {}
        @class_variable_resolution = {}
        @function_variable_resolution = {} #double hash
        @function_argument_resolution = {}
        @loop_number = 0
        @if_number = 0
    end

    def close
        @file.close
    end

    def _is_function_argument(var)
        !@function_argument_resolution[@function_name][var].nil?
    end

    def _is_function_local(var)
        !@function_variable_resolution[@function_name][var].nil?
    end

    def _is_class_variable(var)
        !@class_variable_resolution[var].nil?
    end

    def _is_static_variable(var)
        !@static_resolution[var].nil?
    end

    def _variable_scope(var)
        if self._is_function_argument(var)
            return :argument
        elsif self._is_function_local(var)
            return :function_local
        elsif self._is_class_variable(var)
            return :instance
        else
            return :static
        end
    end

    def _variable_exists(var)
        return (self._is_function_argument(var) or
            self._is_function_local(var) or
            self._is_class_variable(var) or
            self._is_static_variable(var))
    end

    def _variable_type(var)
        unless self._variable_exists(var)
            return nil
        else
            return ([@function_argument_resolution[@function_name][var],
                     @function_variable_resolution[@function_name][var],
                     @class_variable_resolution[var],
                     @static_resolution[var]].first {|x| !(x.nil?)})[:type]
        end
    end

    def _variable_address(var)
        unless self._variable_exists(var)
            return nil
        else
            case self._variable_scope(var)
            when :argument
                return "argument #{@function_argument_resolution[@function_name][var][:index]}"
            when :function_local
                return "local #{@function_variable_resolution[@function_name][var][:index]}"
            when :instance
                return "this #{@class_variable_resolution[var][:index]}"
            when :static
                return "static #{@static_resolution[var][:index]}"
            end
        end
    end

    def _instructions(inst)
        inst = [inst] if inst.kind_of? Array
        inst.each { |x|
            @file.puts x
        }
    end

    def compile
        self.compile_class
    end

    def _to_array(x)
        x.kind_of?(Array) ? x : [x]
    end

    def _is_type(token_type)
        token_type = self._to_array(token_type)
        token_type.include? @tokenizer.current_token_type
    end

    def _is_type_and_value(token_type, value)
        value = self._to_array(value)
        (self._is_type(token_type) and (value.include? @tokenizer.get_value))
    end

    def _check_type(token_type)
        unless (@tokenizer.current_token_type == token_type)
            raise "Type is not #{token_type}, but #{@tokenizer.current_token_type}"
            yield
        end
    end

    def _check_type_and_value(token_type, value)
        self._check_type(token_type) {
            unless (@tokenizer.get_value == value)
                raise "Value is not #{value}, but #{@tokenizer.get_value}"
                yield
            end
        }
    end

    def compile_class
        @tokenizer.advance
        self._check_type_and_value(:keyword, :class)
        @tokenizer.advance
        self._check_type(:identifier)
        @class_name = @tokenizer.get_value
        @tokenizer.advance
        self._check_type_and_value(:symbol, '{')
        while @tokenizer.can_advance
            @tokenizer.advance
            if @tokenizer._is_type_and_value(:keyword, [:static, :field])
                self.compile_class_variable
            elsif @tokenizer._is_type_and_value(:keyword, [:constructor, :function, :method])
                self.compile_subroutine
            elsif @tokenizer._is_type_and_value(:symbol, '}')
                @tokenizer.reverse
                break
            else
                raise "Invalid statement in class context."
            end
        end
        @tokenizer.advance
        self._check_type_and_value(:symbol, '}')
    end

    def _write_class_variable(mode, type, name)
        if mode == :static
            @static_resolution[name] = {}
            @static_resolution[name][:index] = @static_count
            @static_resolution[name][:type] = type
            @static_count += 1
        else
            @class_variable_resolution[name] = {}
            @class_variable_resolution[name][:index] = @class_variable_count
            @class_variable_resolution[name][:type] = type
            @class_variable_count += 1
        end
    end

    def compile_class_variable(type)
        @tokenizer.advance
        self._check_type :identifier
        type_of_var = @tokenizer.get_value
        begin
            @tokenizer.advance
            self._check_type :identifier
            name = self.get_value
            self._write_class_variable(type, type_of_var, name)
            @tokenizer.advance
            self._check_type_and_value :symbol, [',', ';']
        end while @tokenizer.get_value != ';'
    end

    def _call_function(klass, name, num_of_args) #call this only after pushing!!!
        self._instructions "call #{klass}.#{name} #{num_of_args}"
    end

    def _write_function(mode, name, var_type, num_of_locals)
        self._instructions "function #{@class_name}.#{name} #{num_of_locals}"
        case mode
        when :constructor
            self._instructions [
                "push constant #{@class_variable_count}", #allocate memory instead of passing it!
                "call Memory.alloc 1",
                "pop pointer 0"
            ]
        when :method
            self._instructions [
                "push argument 0", #passed
                "pop pointer 0"
            ]
        end
    end

    def _write_function_argument(type, name)
        @function_argument_resolution[@function_name][name][:type] = type
        @function_argument_resolution[@function_name][name][:index] = @function_argument_count[@function_name]
        @function_argument_count[@function_name] += 1
    end

    def _write_local_variable(type, name)
        #no constructor because we don't need it right now
        @function_variable_resolution[@function_name][name][:type] = type
        @function_variable_resolution[@function_name][name][:index] = @function_variable_count[@function_name]
        @function_variable_count[@function_name] += 1
    end

    def _write_function_init(mode, name)
        @method_type[name] = mode
        @function_mode = mode
        @function_name = name
        @function_variable_count[name] = 0
        @function_variable_resolution[name] = {}
        @function_argument_count[name] = 0
        @function_argument_resolution[name] = {}
    end

    def compile_subroutine(mode)
        @tokenizer.advance
        unless self._is_type(:identifier) or self._is_type_and_value(:keyword, [:int, :char, :boolean]) 
            raise "Expected type here"
        end
        var_type = @tokenizer.get_value
        @tokenizer.advance
        self._check_type :identifier
        name = @tokenizer.get_value
        self._write_function_init(mode, name)
        @tokenizer.advance
        self._check_type_and_value :symbol, '('
        self.compile_parameter_list #here, we are just parsing the param list + one more paren
        @tokenizer.advance
        self._write_function(mode, name, var_type, @function_variable_count[@function_name])
        self._check_type_and_value :symbol, '{'
        self.compile_subroutine_body
    end

    def compile_subroutine_body
        @tokenizer.advance
        begin
            @tokenizer.advance
            self.compile_variable_declaration
        end while @tokenizer.get_value == :var
        self.compile_statements
    end

    def compile_parameter_list
        first = true
        begin
            self._check_type_and_value(:symbol, ',') unless first
            first = false
            @tokenizer.advance
            ###need checking
            type = @tokenizer.get_value
            @tokenizer.advance
            self._check_type :identifier
            name = @tokenizer.get_value
            self._write_function_argument(type, name)
            @tokenizer.advance
        end while @tokenizer.get_value != ')'
    end

    def compile_variable_declaration #"var" already parsed
        type = @tokenizer.get_value
        first = true
        begin
            self._check_type_and_value(:symbol, ',') unless first
            first = false
            @tokenizer.advance
            self._check_type :identifier
            name = @tokenizer.get_value
            self._write_local_variable(type, name)
            @tokenizer.advance
        end while @tokenizer.get_value != ';'
    end

    def compile_statements
        @tokenizer.advance
        return if @tokenizer.get_value == '}'
        begin
            mode = @tokenizer.get_value
            self.compile_statement(mode) #reads right into the ;
            @tokenizer.advance
        end while @tokenizer.get_value != '}'
    end

    def compile_statement(mode)
        case mode
        when :let
            self.compile_let
        when :if
            self.compile_if
        when :while
            self.compile_while
        when :do
            self.compile_do
        when :return
            self.compile_return
        end
    end

    def compile_children_of(tree)
        tree.children.each { |child|
            self.compile_expression_tree child
        }
    end

    def compile_expression_tree(tree)
        if tree.children.size == 0
            case tree.type
            when :integer_terminal
                self._instructions "push constant #{tree.value}"
            when :string_terminal
                self._instructions [
                    "push constant #{tree.value.size}",
                    "call String.new 1"
                ]
                tree.value.each_byte { |char_ascii|
                    self._instructions [
                        "push constant #{char_ascii}",
                        "call String.appendChar 2"
                    ]
                }
            when :variable
                self._instructions "push #{self._variable_address tree.value}"
            when :keyword_constant
                push_instruction = case tree.value
                                   when :true
                                       "push constant 1"
                                   when :false
                                       "push constant 0"
                                   when :this
                                       "push pointer 0"
                                   when :null
                                       "push constant 0" ###correct?
                                   end
                self._instructions push_instruction
            end
        else
            #if it's a method, not ctor or func, note that we have already pushed the caller as one of the args
            self.compile_children_of tree
            case tree.type
            when :operator
                if OPERATIONS[:binary].include? tree.value and !(tree.value == '-' and tree.children.size == 1)
                    self._instructions OPERATOR_MAP[:binary][tree.value]
                elsif OPERATIONS[:unary].include? tree.value
                    self._instructions OPERATOR_MAP[:unary][tree.value]
                elsif tree.value == '['
                    self._instructions [
                        "add",
                        "pop pointer 1",
                        "push that 0"
                    ]
                else
                    raise "Invalid operator!"
                end
            when :function_call
                self._instructions "call #{tree.value} #{tree.children.size}"
            end
        end
    end

    def compile_do #already parsed mode, will parse semicolon
        @tokenizer.advance
        tree = self.compile_subroutine_call
        self.compile_expression_tree tree
    end

    def compile_subroutine_call
        self._check_type :identifier
        first = @tokenizer.get_value
        @tokenizer.advance
        if @tokenizer.get_value == '.'
            @tokenizer.advance
            second = @tokenizer.get_value
            type = self._variable_exists(first) ? self._variable_type(first) : false
            @tokenizer.advance
            tree = JackExpressionTree.new nil, (type ? "#{type}.#{second}" : "#{first}.#{second}"), :function
            if self._variable_exists(first)
                tree.add_subtree first
            end
        else
            if first != @class_name
                tree = JackExpressionTree.new nil, "#{@class_name}.#{first}", :function
            else
                tree = JackExpressionTree.new nil, "#{@class_name}.new", :constructor
            end
            tree.add_subtree(:this) if @method_type[first] == method
        end
        self._check_type_and_value :symbol, '('
        self.compile_expression_list(tree) #add things to tree
        return tree
    end

    def compile_let
        @tokenizer.advance
        self._check_type :identifier
        var = @tokenizer.get_value
        @tokenizer.advance
        if @tokenizer.get_value == '['
            index_tree = self.compile_expression
            self._check_type_and_value :symbol, ']'
            @tokenizer.advance
            self._check_type_and_value :symbol, '='
            rhs_tree = self.compile_expression
            self.compile_expression_tree rhs_tree
            self._instructions "push #{self._variable_address var}"
            self.compile_expression_tree index_tree
            self._instructions [
                "add",
                "pop pointer 1",
                "pop that 0"
            ]
        else
            self._check_type_and_value :symbol, '='
            @tokenizer.advance
            if @tokenizer.get_value == "new"
                @tokenizer.advance
            end
            tree = self.compile_expression
            self.compile_expression_tree tree
            self._instructions "pop #{self._variable_address var}"
        end
    end

    def _get_loop_labels
        num = @loop_number
        @loop_number += 1
        return "#{@class_name}.loop_#{num}.start", "#{@class_name}.loop_#{num}.end"
    end

    def compile_while
        @tokenizer.advance
        self._check_type_and_value :symbol, '('
        condition_tree = self.compile_expression
        @tokenizer.advance
        self._check_type_and_value :symbol, '{'
        @tokenizer.advance
        start_label, end_label = self._get_loop_labels
        self._instructions "label #{start_label}"
        self.compile_expression_tree condition_tree
        self._instructions [
            "not",
            "if-goto #{end_label}"
        ]
        self.compile_statements
        self._instructions [
            "goto #{start_label}",
            "label #{end_label}"
        ]
    end

    def compile_return
        @tokenizer.advance
        if @tokenizer.get_value != ';'
            return_tree = self.compile_expression
            #push the thing and return
            self.compile_expression_tree return_tree
        end
        self._instructions "return"
    end

    def _get_if_label
        label = @if_label
        @if_label += 1
        "#{@class_name}.if_#{label}"
    end

    def compile_if
        @tokenizer.advance
        self._check_value_and_type :symbol, '('
        if_conditional_tree = self.compile_expression
        @tokenizer.advance
        self._check_value_and_type :symbol, '{'
        @tokenizer.advance
        label = self._get_if_label
        self.compile_expression_tree if_conditional_tree
        self._instructions [
            "not",
            "if-goto #{label}"
        ]
        self.compile_statements
        self._instructions "label #{label}"
    end

    def compile_expression
        #it's just term op term op term op term... keep compiling terms until the terminal operator ) or , hits
        tree = self.compile_term
        @tokenizer.advance
        until [')', ',', ']', ';'].include? @tokenizer.get_value
            tree = JackExpressionTree.new(nil, @tokenizer.get_value, :operator, [tree, self.compile_term]) #tokenizer.get_value is the operator
            @tokenizer.advance
        end
        return tree
    end

    def compile_term #returns tree.  we actually don't need a terminal operator to tell us we're done here
        value = @tokenizer.get_value
        case @tokenizer.current_token_type
        when :integer, :string
            tree = JackExpressionTree.new(nil, value, :constant)
        when :keyword
            if KEYWORD_CONSTANTS.include? value
                tree = JackExpressionTree.new(nil, value, :keyword_constant)
            else
                raise "Invalid keyword."
            end
        when :identifier
            @tokenizer.advance
            next_symbol = @tokenizer.get_value
            @tokenizer.reverse
            if OPERATORS[:binary].include? next_symbol
                tree = JackExpressionTree.new(nil, value, :variable)
            else
                case next_symbol
                when ')', ',', ']', ';'
                    tree = JackExpressionTree.new(nil, value, :variable)
                when '['
                    tree = JackExpressionTree.new(nil, '[', :operator, [JackExpressionTree.new(nil, value, :variable),
                                                                        self.compile_expression])
                when '.', '('
                    tree = self.compile_subroutine_call
                end
            end
        when :symbol
            if OPERATORS[:unary].include? value
                tree = JackExpressionTree.new(nil, value, false, [self.compile_term])
            elsif value == '('
                tree = self.compile_expression
            else
                raise "Invalid starting symbol."
            end
        end
        return tree
    end

    def compile_expression_list(tree)
        begin
            @tokenizer.advance
            tree.add self.compile_expression
        end while @tokenizer.get_value != ')'
    end
end

class Jack
    def initialize(folder_name)
        Dir.foreach(folder_name) { |file|
            next unless (File.file?(file) and file.end_with?(".jack"))
            self.compile file
        }
    end

    def compile(file)
        tokenizer = JackTokenizer.new file
        compiler = JackCompiler.new tokenizer, file
        compiler.compile
    end
end

jack = Jack.new ARGF.argv.first
jack.compile
