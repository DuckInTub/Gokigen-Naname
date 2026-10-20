:- [read].

% gokigen(+Constraints, -SolveBoard)
gokigen(Constraints, SolvedBoard) :-
    length(Constraints, IntRows), % Intersection rows
    nth0(0, Constraints, FirstRow),
    length(FirstRow, IntCols), % Intersection cols

    % Generate Disjoint Sets Matrix
    length(DS, IntRows),
    maplist(new_DS_row(IntCols), DS),

    % Generate Intersection Matrix
    length(Intersections, IntRows),
    maplist(new_I_row(IntCols), Intersections),

    % Constrain the board: 
    % 1. Set border cells to 0.
    border_zeros(Intersections),
    % 2. Propagate state deducible from constraints across the board. (Fix-point iteration)
    propagate(Constraints, Intersections),

    % At this point the board contains all "easily" deducible
    % information that a human would deduce.
    !,

    % Backtrack over the cells that can not be easily deduced.
    backtrack(Constraints, DS, Intersections, SolvedBoard).

% TODO: Replace pairs with - notation.
backtrack([_], [_], [_], []).
backtrack([TopC, BotC | RestC], [TopDS, BotDS | RestDS], [TopI, BotI | RestI], [SolvedRow | RestBoard]) :-
    backtrack_row(rp(TopC, BotC), rp(TopDS, BotDS), rp(TopI, BotI), SolvedRow),
    backtrack([BotC | RestC], [BotDS | RestDS], [BotI | RestI], RestBoard).

backtrack_row(
    rp([_], [_]),
    rp([_], [_]),
    rp([_], [_]),
    []
).
backtrack_row(
    rp([TLC, TRC | TopC], [BLC, BRC | BotC]),
    rp([TLDS, TRDS | TopDS], [BLDS, BRDS | BotDS]),
    rp([TLI, TRI | TopI], [BLI, BRI | BotI]),
    [Slant | RestSolvedRow]
) :-
    TLI = i(_, _, _, TLV),
    TRI = i(_, _, TRV, _),
    BLI = i(_, BLV, _, _),
    BRI = i(BRV, _, _, _),

    place(Slant, sets(TLDS, TRDS, BLDS, BRDS), vals(TLV, TRV, BLV, BRV)),

    % Update the values of the local intersections.
    % NOTE: We do not do a propagation over the whole board since
    % that is too expensive in this hot backtracking loop.
    maplist(force_intersection, [TLC, TRC, BLC, BRC], [TLI, TRI, BLI, BRI]),

    backtrack_row(
        rp([TRC | TopC], [BRC | BotC]),
        rp([TRDS | TopDS], [BRDS | BotDS]),
        rp([TRI | TopI], [BRI | BotI]),
        RestSolvedRow
    ).

place(/, sets(_, TR, BL, _), vals(0, 1, 1, 0)) :-
    TR \== BL,
    TR = BL.
place(\, sets(TL, _, _, BR), vals(1, 0, 0, 1)) :-
    TL \== BR,
    TL = BR.

neg(In, Out) :-
    nonvar(In),
    var(Out),
    !,
    Out is 1 - In.
neg(In, Out) :-
    nonvar(Out),
    var(In),
    !,
    In is 1 - Out.
neg(_, _).

deduce([_]).
deduce([TopRow, BotRow | Rest]) :-
    deduce_rows(TopRow, BotRow),
    deduce([BotRow | Rest]).

deduce_rows([_], [_]).
deduce_rows([TLI, TRI | TopRest], [BLI, BRI | BotRest]) :-
    % WARN: Because of `border_zeros` it is only safe to deduce Center cells.
    % These are the real, visible cells of the board.
    TLI = i(_, _, _, Center),
    TRI = i(_, _, NegCenter, _),
    BLI = i(_, NegCenter, _, _),
    BRI = i(Center, _, _, _),

    neg(Center, NegCenter),

    deduce_rows([TRI | TopRest], [BRI | BotRest]).

new_DS_row(0, []).
new_DS_row(N, [_ | Rest]) :-
    N > 0,
    N1 is N - 1,
    new_DS_row(N1, Rest).

new_I_row(0, []).
new_I_row(N, [i(_, _, _, _) | Rest]) :-
    N > 0,
    N1 is N - 1,
    new_I_row(N1, Rest).

border_zeros(Intersections) :-
    Intersections = [FirstRow | _],
    last(Intersections, LastRow),
    maplist(top_zero, FirstRow),
    maplist(bot_zero, LastRow),
    maplist(left_zero, Intersections),
    maplist(right_zero, Intersections).

top_zero(i(0, 0, _, _)).
bot_zero(i(_, _, 0, 0)).
left_zero([i(0, _, 0, _) | _]).
right_zero(Row) :-
    last(Row, i(_, 0, _, 0)).

propagate(Constraints, Intersections) :-
    term_variables(Intersections, Before),
    maplist(maplist(force_intersection), Constraints, Intersections),
    deduce(Intersections),
    term_variables(Intersections, After),
    (After == Before -> true; propagate(Constraints, Intersections)).

force_intersection(Constraint, _) :-
    var(Constraint),
    !.

force_intersection(Constraint, i(TL, TR, BL, BR)) :-
    nonvar(Constraint),
    val(TL, V1, U1),
    val(TR, V2, U2),
    val(BL, V3, U3),
    val(BR, V4, U4),
    Connected is V1 + V2 + V3 + V4,
    Unbound is U1 + U2 + U3 + U4,
    Possible is Connected + Unbound,

    Connected =< Constraint,
    Constraint =< Possible,

    force(Constraint, Connected, Possible, [TL, TR, BL, BR]).


val(Var, 0, 1) :-
    var(Var).
val(Var, Var, 0) :-
    nonvar(Var).

%! force(+Constraint, +Connected, +Possible, +Edges:list)
% Constraint == "Already connected"
force(Constraint, Constraint, _, Edges) :-
    !,
    term_variables(Edges, Vars),
    maplist(=(0), Vars).
% Constraint == "Max possible"
force(Constraint, _, Constraint, Edges) :-
    !,
    term_variables(Edges, Vars),
    maplist(=(1), Vars).
force(_, _, _, _).

main :-
    read_constraints(Constraints),
    gokigen(Constraints, Board),
    write_board(Board).