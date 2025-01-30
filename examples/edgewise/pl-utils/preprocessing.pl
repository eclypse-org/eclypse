:-['requirements.pl', 'costs.pl'].
:- dynamic deployed/2.
%:- ['../data/apps/arFarming.pl', '../data/infrs/infr32-42.pl'].

:- set_prolog_flag(answer_write_options,[max_depth(0)]). % write answers' text entirely
:- set_prolog_flag(stack_limit, 32 000 000 000).
:- set_prolog_flag(last_call_optimisation, true).

preprocess(App, Compatibles) :-
    \+ deployed(App, _),
    application(App, Functions, Services), 
    checkThings,
    append(Functions, Services, Components),
    findCompatibles(Components, Compatibles).
preprocess(App, Compatibles) :-
    deployed(App, Placement),
    checkThings,
    crStep(Placement, Compatibles).

crStep(P, Compatibles) :- crStep(P, [], Compatibles).
crStep([(C,N)|P], POk, [(C,[(N,Cost)])|Cs]) :-
    componentPlacement(C, N, P), qosOK(C, N, POk),
    lightNodeOK(C, N, Cost),
    crStep(P, [(C,N)|POk], Cs).
crStep([(C,N)|P], POk, [(C,[Comp|Atibles])|Cs]) :-
    \+ ( componentPlacement(C, N, P); qosOK(C, N, POk) ), 
    findall((N, Cost), lightNodeOK(C, N, Cost), [Comp|Atibles]),
    crStep(P, POk, Cs).
crStep([], _, []).

checkThings :-
    findall(T, thingInstance(T, _), Things),
    findall(T, (node(_, _, _, _, IoTCaps), member(T, IoTCaps)), IoT),
    subset(Things, IoT).

componentPlacement(F, N, P) :-
    functionInstance(F, FId, _), function(FId, SWPlat, (Arch,HWReqs)),
    node(N, SWCaps, (Arch,HWCaps), _, _), 
    requirements(FId, N), 
    member(SWPlat, SWCaps),
    hwOK(N, HWCaps, HWReqs, P).
componentPlacement(S, N, P) :-
    serviceInstance(S, SId), service(SId, SWReqs, (Arch,HWReqs)),
    node(N, SWCaps, (Arch,HWCaps), _, _), 
    requirements(SId, N), 
    subset(SWReqs, SWCaps),
    hwOK(N, HWCaps, HWReqs, P).

qosOK(C, N, P) :- 
    findall(DF, relevant(C, N, P, DF), DataFlows), 
    checkDF(DataFlows, [(C,N)|P]).

hwOnN(N, Ps, HW) :- serviceInstance(S, SId), service(SId,_,(_,HW)), member((S,N), Ps).
hwOnN(N, Ps, HW) :- functionInstance(F, FId,_), function(FId,_,(_,HW)), member((F,N), Ps).

hwOK(N, HWCaps, HWReqs, P) :- 
    findall(H, hwOnN(N, P, H), Hs), sum_list(Hs, UsedHW),
    hwTh(T), HWCaps >= HWReqs + UsedHW + T.

relevant(C, N, P, (N, M, Lat, BW, Sec)):-
    dataFlow(C, C1, _, Sec, Size, Rate, Lat),
    (member((C1,M), P); node(M, _, _, _, IoTCaps), member(C1, IoTCaps)),
    BW is Size*Rate.
relevant(C, N, _, (M, N, Lat, BW, Sec)):-
    dataFlow(C1, C, _, Sec, Size, Rate, Lat),
    node(M, _, _, _, IoTCaps), member(C1, IoTCaps),
    BW is Size*Rate.

checkDF([(N1,N2, ReqLat, _, SecReqs)|DFs], [(C,N)|P]) :-
    secOK(N1, N2, SecReqs),
    link(N1, N2, FeatLat, FeatBW),
    FeatLat =< ReqLat,
    bwOK(C, N, FeatBW, P),
    checkDF(DFs, [(C,N)|P]).
checkDF([], _).

secOK(N1, N2, SecReqs) :-
    node(N1, _, _, SecCaps1, _), subset(SecReqs, SecCaps1),
    node(N2, _, _, SecCaps2, _), subset(SecReqs, SecCaps2).

bwOK(C, N, FeatBW, P):-
    findall(BW, relevant(C, N, P, (_,_,_,BW,_)), BWs), sum_list(BWs, OkAllocBW), 
    bwTh(T), FeatBW >= OkAllocBW + T.


findCompatibles([C|Cs], [(C,[Comp|Atibles])|Rest]):-
    findCompatibles(Cs, Rest),
    findall((N, Cost), lightNodeOK(C, N, Cost), [Comp|Atibles]).  
findCompatibles([],[]).

lightNodeOK(S, N, SCost) :-
    serviceInstance(S, SId), service(SId, SWReqs, (Arch, HWReqs)),
    node(N, SWCaps, (Arch, HWCaps), _, _),
    requirements(SId, N),
    subset(SWReqs, SWCaps), HWCaps >= HWReqs,
    nodeType(N, Type), cost(Type, S, SCost).

lightNodeOK(F, N, FCost) :-
    functionInstance(F, FId, _), function(FId, SWPlatform, (Arch, HWReqs)),
    node(N, SWCaps, (Arch, HWCaps), _, _),
    requirements(FId, N),
    member(SWPlatform, SWCaps), HWCaps >= HWReqs,
    nodeType(N, Type), cost(Type, F, FCost).