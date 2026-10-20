read_constraints(Constraints) :-
    read_line_to_string(user_input, String),
    number_string(N, String),
    Rows is N + 1,
    length(Constraints, Rows),
    maplist(read_constraints(user_input), Constraints).

read_constraints(Stream, Row) :-
    read_line_to_codes(Stream, Codes),
    maplist(parse_char, Codes, Row).

parse_char(0x2E, _).
parse_char(Code, N) :-
    Code >= 0x30,
    Code =< 0x39,
    N is Code - 0x30.

write_board(Board) :-
    maplist(writerow, Board).

writerow(Row) :-
    maplist(write, Row),
    nl.

print_deduced([_]).
print_deduced([TopRow, BotRow | Rest]) :-
    print_deduced_row(TopRow, BotRow),
    nl,
    print_deduced([BotRow | Rest]).

print_deduced_row([_], [_]).
print_deduced_row([TLI, TRI | TopRest], [BLI, BRI | BotRest]) :-
    TLI = i(_, _, _, TLV),
    TRI = i(_, _, TRV, _),
    BLI = i(_, BLV, _, _),
    BRI = i(BRV, _, _, _),

    write_slant(vals(TLV, TRV, BLV, BRV)),
    
    print_deduced_row([TRI | TopRest], [BRI | BotRest]).

write_slant(vals(0, 1, 1, 0)) :-
    write('/').
write_slant(vals(1, 0, 0, 1)) :-
    write('\\').
write_slant(_) :-
    !,
    write('.').