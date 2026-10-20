:- use_module(library(clpfd)).

% gokigen(+Constraints, -SolvedBoard)
gokigen(Constraints, SolvedBoard) :-
    length(Constraints, IntRows),
    Constraints = [FirstRow | _],
    length(FirstRow, IntCols),

    % Generate Disjoint Sets Matrix
    length(DS, IntRows),
    maplist(new_DS_row(IntCols), DS),

    % Generate Intersection Matrix
    length(Intersections, IntRows),
    maplist(new_I_row(IntCols), Intersections),

    % Set up and constrain the board.
    border_zeros(Intersections),
    constrain_intersections(Constraints, Intersections),
    unify_edges(Intersections),

    !,
    backtrack(DS, Intersections, SolvedBoard).

backtrack([_], [_], []).
backtrack([TopDS, BotDS | RestDS], [TopI, BotI | RestI], [SolvedRow | RestBoard]) :-
    backtrack_row(rp(TopDS, BotDS), rp(TopI, BotI), SolvedRow),
    backtrack([BotDS | RestDS], [BotI | RestI], RestBoard).

backtrack_row(
    rp([_], [_]),
    rp([_], [_]),
    []
).
backtrack_row(
    rp([TLDS, TRDS | TopDS], [BLDS, BRDS | BotDS]),
    rp([TLI, TRI | TopI], [BLI, BRI | BotI]),
    [Slant | RestSolvedRow]
) :-
    TLI = i(_, _, _, TLV),
    TRI = i(_, _, TRV, _),
    BLI = i(_, BLV, _, _),
    BRI = i(BRV, _, _, _),

    place(Slant, sets(TLDS, TRDS, BLDS, BRDS), vals(TLV, TRV, BLV, BRV)),

    backtrack_row(
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

constrain_intersections([], []).
constrain_intersections(Constraints, Intersections) :-
    maplist(maplist(constrain_vertex), Constraints, Intersections).

constrain_vertex(C, _) :-
    var(C),
    !.
constrain_vertex(C, i(TL, TR, BL, BR)) :-
    [TL, TR, BL, BR] ins 0..1,
    TL + TR + BL + BR #= C.

unify_edges([_]).
unify_edges([TopRow, BotRow | Rest]) :-
    unify_edges_row(TopRow, BotRow),
    unify_edges([BotRow | Rest]).

unify_edges_row([_], [_]).
unify_edges_row([TLI, TRI | TopRest], [BLI, BRI | BotRest]) :-
    % NOTE: Because of `border_zeros` it is only safe to constrain Center cells.
    TLI = i(_, _, _, Center),
    TRI = i(_, _, NegCenter, _),
    BLI = i(_, NegCenter, _, _),
    BRI = i(Center, _, _, _),

    [Center, NegCenter] ins 0..1,
    Center + NegCenter #= 1,

    unify_edges_row([TRI | TopRest], [BRI | BotRest]).

:- [read].

main :-
    read_constraints(Constraints),
    gokigen(Constraints, Board),
    write_board(Board).