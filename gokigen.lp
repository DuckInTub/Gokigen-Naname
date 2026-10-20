% constraint(Row, Col, Deg): True iff there is a constraint at intersection (Row, Col) of degree Deg.
% NOTE: Defined and important from a problem file.

cell(0..R-1, 0..C-1) :- rows(R), cols(C).
intersection(0..R, 0..C) :- rows(R), cols(C).

1 {slant((slash;backslash), R, C)} 1 :- cell(R, C).

% touches(R, C, IR, IC): 
% map which cell (R, C) touches what intersections (IR, IC).
% Backslash:
touches(R, C, R, C) :- slant(backslash, R, C).
touches(R, C, R+1, C+1) :- slant(backslash, R, C).
% Slash:
touches(R, C, R+1, C) :- slant(slash, R, C).
touches(R, C, R, C+1) :- slant(slash, R, C).

:- 
    constraint(ConR, ConC, Deg),
    #count {R, C: touches(R, C, ConR, ConC)} != Deg.


edge(R1, C1, R2, C2, CR, CC) :-
    touches(CR, CC, R1, C1),
    touches(CR, CC, R2, C2),
    (R1, C1) != (R2, C2).

path(R1, C1, R2, C2, CR, CC) :-
    edge(R1, C1, R2, C2, CR, CC).

path(R1, C1, R3, C3, CR2, CC2) :-
    path(R1, C1, R2, C2, CR1, CC1),
    edge(R2, C2, R3, C3, CR2, CC2),
    (CR1, CC1) != (CR2, CC2).

:- path(R, C, R, C, _, _).

#show slant/3.