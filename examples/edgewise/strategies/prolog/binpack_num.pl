% :-['../data/infrs/infr32.pl', '../data/apps/speakToMe.pl'].
:-['../pl-utils/requirements.pl', '../pl-utils/costs.pl'].

:- set_prolog_flag(answer_write_options,[max_depth(0)]). % write answers' text entirely
:- set_prolog_flag(stack_limit, 32 000 000 000).
:- set_prolog_flag(last_call_optimisation, true).

stats(App, Placement, Cost, Bins, Infs, Time) :-
    statistics(inferences, InfA),
        statistics(cputime, TimeA),
            best(App, Placement, Cost),
            countDistinct(Placement, Bins),
        statistics(cputime, TimeB),
    statistics(inferences, InfB),

    Infs is InfB - InfA,
    Time is TimeB - TimeA.

best(App, Placement, Cost) :-
    application(App, Functions, Services),
    checkThings, 
    ranking(Functions, Services, RankedComps),  % RankedComps:  [(Rank, Comp)|Rest] --> sort "Comp" by increasing HWReqs
    findCompatibles(RankedComps, Components),   % Components:   [(Comp, Compatibles)|Rest]--> sort "Compatibles" nodes by decreasing HWCaps
    findBudget(Components, Budget),
    placement(Components, Placement, Budget, Cost),
    qosOK(Placement).

findBudget(C, B) :- findBudget(C, 0, B).
findBudget([(_, Comps)|Cs], OldB, NewB) :-
    maxCost(Comps, CB), TmpB is OldB + CB,
    findBudget(Cs, TmpB, NewB).
findBudget([], B, B).

maxCost(Comps, MaxCost) :- member((MaxCost,_,N), Comps), \+ (member((CostM,_,M), Comps), dif(N,M), CostM > MaxCost).

checkThings :-
    findall(T, thingInstance(T, _), Things),
    findall(T, (node(_, _, _, _, IoTCaps), member(T, IoTCaps)), IoT),
    subset(Things, IoT).

countDistinct(P, L) :-
    findall(N, distinct(member((_,N), P)), S),
    sort(S, Ss), length(Ss, L).

findCompatibles(Compatibles, Components) :- findCompatibles(Compatibles, [], Components).
findCompatibles([(_,C)|Cs], OldC, NewC):-
    findall((Cost, H, M), lightNodeOK(C, M, H, Cost), [Comp|Atibles]), 
    sort([Comp|Atibles], SCompatibles), % cannot be empty
    findCompatibles(Cs, [(C,SCompatibles)|OldC], NewC).
findCompatibles([], C, C).

lightNodeOK(S,N,H,SCost) :-
    serviceInstance(S, SId), service(SId, _, (Arch, HWReqs)),
    node(N, _, (Arch, HWCaps), _, _),
    HWCaps >= HWReqs, H is 1/HWCaps, % H used to sort Compatibles (ascending H --> descending HWCaps)) 
    nodeType(N, Type), cost(Type, S, SCost).

lightNodeOK(F,N,H,FCost) :-
    functionInstance(F, FId, _), function(FId, _, (Arch, HWReqs)),
    node(N, _, (Arch, HWCaps), _, _),
    HWCaps >= HWReqs, H is 1/HWCaps,
    nodeType(N, Type), cost(Type, F, FCost).

placement(Cs, Placement, Budget, NewCost) :- placement(Cs, [], Placement, Budget, 0, NewCost).

placement([(C, Comps)|Cs], OldP, NewP, Budget, OldCost, NewCost) :-
    componentPlacement(C, Comps, N, OldP, CCost),
    TCost is OldCost + CCost, TCost < Budget,
    placement(Cs, [(C,N)|OldP], NewP, Budget, TCost, NewCost).
placement([], P, P, _, Cost, Cost).

componentPlacement(F, Comps, N, Ps, FCost) :-
    functionInstance(F, FId, _), function(FId, _, HWReqs),
    member((_,N), Ps), member((FCost,_,N), Comps),
    compatible(N, HWReqs, Ps).
componentPlacement(F, Comps, N, Ps, FCost) :-
    functionInstance(F, FId, _), function(FId, _, HWReqs),
    member((FCost,_,N), Comps), \+ member((_,N),Ps),
    compatible(N, HWReqs, Ps).

componentPlacement(S, Comps, N, Ps, SCost) :-
    serviceInstance(S, SId), service(SId, _, HWReqs),
    member((_,N), Ps), member((SCost,_,N), Comps),
    compatible(N, HWReqs, Ps).
componentPlacement(S, Comps, N, Ps, SCost) :-
    serviceInstance(S, SId), service(SId, _, HWReqs),
    member((SCost,_,N), Comps), \+ member((_,N),Ps),
    compatible(N, HWReqs, Ps).

compatible(N, (Arch,HWReqs), Ps) :- node(N, _, (Arch, HWCaps), _, _), hwOK(N, HWCaps, HWReqs, Ps).

hwOK(N,HWCaps,HWReqs,Ps) :-
    findall(HW, hwOnN(N, Ps, HW), HWs), sum_list(HWs,TotHW),
    hwTh(T), HWCaps >= TotHW + HWReqs + T.

hwOnN(N, Ps, HW) :- serviceInstance(S, SId), service(SId,_,(_,HW)), member((S,N), Ps).
hwOnN(N, Ps, HW) :- functionInstance(F, FId,_), function(FId,_,(_,HW)), member((F,N), Ps).

qosOK(Ps) :- findall((N1N2, Lat), relevant(N1N2, Ps, Lat, _), DataFlows), checkDF(DataFlows, Ps).

checkDF([((N1,N2),ReqLat)|DFs], Ps) :-
    (link(N1, N2, FeatLat, FeatBW); link(N2, N1, FeatLat, FeatBW)),
    FeatLat =< ReqLat, bwOK((N1,N2), FeatBW, Ps),
    checkDF(DFs, Ps).
checkDF([], _).

bwOK(N1N2, FeatBW, Ps):-
    findall(BW, relevant(N1N2, Ps, _, BW), BWs), sum_list(BWs, OkAllocBW), 
    bwTh(T), FeatBW >= OkAllocBW + T.

relevant((N1,N2), Ps, Lat, BW):-
    dataFlow(T1, T2, _, _, Size, Rate, Lat),
    (member((T1,N1), Ps); node(N1, _, _, _, IoTCaps), member(T1, IoTCaps)),
    (member((T2,N2), Ps); node(N2, _, _, _, IoTCaps), member(T2, IoTCaps)),
    BW is Size*Rate.