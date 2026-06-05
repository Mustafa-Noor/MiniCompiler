program GCD;
var
    x, y: integer;
    result: integer;
    arr: array [1..10] of integer;

function gcd(a, b: integer): integer;
begin
    if b = 0 then
        gcd := a
    else
        gcd := gcd(b, a mod b)
end;

begin
    { Read two integers }
    read(x, y);
    
    { Compute and display GCD }
    result := gcd(x, y);
    write(result);
    
    { Loop example }
    while x > 0 do
    begin
        x := x - 1;
        y := y + 1
    end;
    
    { Conditional with operators }
    if result > 100 then
        result := result div 2
    else
    begin
        if result > 50 then
            result := result mod 10
        else
            result := result and 7
    end;
    
end.
