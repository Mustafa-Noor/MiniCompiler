program GCD;
var
    x, y: integer;
    result: integer;

function gcd(a, b: integer): integer;
begin
    if b = 0 then
        gcd := a
    else
        gcd := gcd(b, a mod b)
end;

begin
    read(x, y);
    result := gcd(x, y);
    write(result)
end.