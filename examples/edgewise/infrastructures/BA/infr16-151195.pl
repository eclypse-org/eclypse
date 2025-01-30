bwTh(3).
hwTh(1).

node(n14, [gcc, ubuntu], (arm64, 608), [access_logs, authentication, process_isolation, permission_model, resource_monitoring, user_data_isolation, certificates, firewall, enc_iot, node_isolation, network_ids, public_key_crypto, wireless_security, backup, enc_storage, obfuscated_storage, access_control, anti_tampering, audit], []).
node(n3, [js, python], (arm64, 512), [access_logs, authentication, resource_monitoring, firewall, enc_iot, node_isolation, public_key_crypto, wireless_security, enc_storage, obfuscated_storage, anti_tampering], [soil, echoDot]).
node(n2, [python, gcc, ubuntu], (x86, 384), [access_logs, authentication, resource_monitoring, firewall, enc_iot, node_isolation, public_key_crypto, wireless_security, enc_storage, obfuscated_storage, anti_tampering], [iphoneXS, piCamera1]).
node(n1, [mySQL, ubuntu, python], (x86, 608), [access_logs, authentication, resource_monitoring, firewall, enc_iot, node_isolation, public_key_crypto, wireless_security, enc_storage, obfuscated_storage, anti_tampering], [cam11]).
node(n8, [gcc, ubuntu], (x86, 608), [access_logs, authentication, process_isolation, permission_model, resource_monitoring, user_data_isolation, certificates, firewall, enc_iot, node_isolation, network_ids, public_key_crypto, wireless_security, backup, enc_storage, obfuscated_storage, access_control, anti_tampering, audit], [heat]).
node(n4, [mySQL, gcc, js, python], (arm64, 384), [access_logs, authentication, process_isolation, permission_model, resource_monitoring, user_data_isolation, certificates, firewall, enc_iot, node_isolation, network_ids, public_key_crypto, wireless_security, backup, enc_storage, obfuscated_storage, access_control, anti_tampering, audit], [piCamera2, nutrient]).
node(n9, [mySQL], (x86, 928), [access_logs, authentication, resource_monitoring, firewall, enc_iot, node_isolation, public_key_crypto, wireless_security, enc_storage, obfuscated_storage, anti_tampering], []).
node(n5, [ubuntu, python, mySQL], (x86, 448), [access_logs, authentication, resource_monitoring, firewall, enc_iot, node_isolation, public_key_crypto, wireless_security, enc_storage, obfuscated_storage, anti_tampering], [energy]).
node(n15, [mySQL, js], (arm64, 448), [access_logs, authentication, resource_monitoring, firewall, enc_iot, node_isolation, public_key_crypto, wireless_security, enc_storage, obfuscated_storage, anti_tampering], []).
node(n13, [ubuntu, mySQL, python, js, gcc], (x86, 672), [access_logs, authentication, process_isolation, permission_model, resource_monitoring, restore_point, user_data_isolation, certificates, firewall, enc_iot, node_isolation, network_ids, public_key_crypto, backup, enc_storage, access_control, anti_tampering, audit], []).
node(n7, [python], (arm64, 640), [access_logs, authentication, resource_monitoring, firewall, enc_iot, node_isolation, public_key_crypto, wireless_security, enc_storage, obfuscated_storage, anti_tampering], [cam12]).
node(n11, [ubuntu, gcc, python, js], (x86, 672), [access_logs, authentication, process_isolation, permission_model, resource_monitoring, user_data_isolation, certificates, firewall, enc_iot, node_isolation, network_ids, public_key_crypto, wireless_security, backup, enc_storage, obfuscated_storage, access_control, anti_tampering, audit], []).
node(n6, [ubuntu], (arm64, 640), [access_logs, authentication, resource_monitoring, firewall, enc_iot, node_isolation, public_key_crypto, wireless_security, enc_storage, obfuscated_storage, anti_tampering], [cam22, cam21]).
node(n0, [mySQL, python, ubuntu, js], (x86, 448), [access_logs, authentication, process_isolation, permission_model, resource_monitoring, user_data_isolation, certificates, firewall, enc_iot, node_isolation, network_ids, public_key_crypto, wireless_security, backup, enc_storage, obfuscated_storage, access_control, anti_tampering, audit], [arViewer, water]).
node(n10, [python, ubuntu, mySQL], (x86, 608), [access_logs, authentication, process_isolation, permission_model, resource_monitoring, user_data_isolation, certificates, firewall, enc_iot, node_isolation, network_ids, public_key_crypto, wireless_security, backup, enc_storage, obfuscated_storage, access_control, anti_tampering, audit], []).
node(n12, [ubuntu, mySQL, python, js, gcc], (arm64, 416), [access_logs, authentication, process_isolation, permission_model, resource_monitoring, restore_point, user_data_isolation, certificates, firewall, enc_iot, node_isolation, network_ids, public_key_crypto, backup, enc_storage, access_control, anti_tampering, audit], []).

link(n3, n4, 18.0, 24).
link(n4, n3, 18.0, 24).
link(n7, n9, 11.0, 391).
link(n9, n7, 11.0, 391).
link(n11, n15, 18.0, 289).
link(n15, n11, 18.0, 289).
link(n2, n15, 19.0, 85).
link(n15, n2, 19.0, 85).
link(n3, n5, 16.0, 473).
link(n5, n3, 16.0, 473).
link(n5, n13, 13.0, 168).
link(n13, n5, 13.0, 168).
link(n2, n5, 10, 180).
link(n5, n2, 10, 180).
link(n4, n6, 11.0, 146).
link(n6, n4, 11.0, 146).
link(n12, n13, 16.0, 352).
link(n13, n12, 16.0, 352).
link(n2, n10, 13, 356).
link(n10, n2, 13, 356).
link(n0, n13, 8, 58).
link(n13, n0, 8, 58).
link(n5, n9, 4, 466).
link(n9, n5, 4, 466).
link(n9, n11, 5, 253).
link(n11, n9, 5, 253).
link(n10, n13, 16.0, 402).
link(n13, n10, 16.0, 402).
link(n8, n11, 10.0, 390).
link(n11, n8, 10.0, 390).
link(n9, n12, 11.0, 382).
link(n12, n9, 11.0, 382).
link(n1, n11, 12, 204).
link(n11, n1, 12, 204).
link(n0, n0, 0.0, inf).
link(n6, n15, 12, 255).
link(n15, n6, 12, 255).
link(n15, n15, 0.0, inf).
link(n1, n14, 8, 68).
link(n14, n1, 8, 68).
link(n1, n6, 11, 233).
link(n6, n1, 11, 233).
link(n3, n6, 7, 239).
link(n6, n3, 7, 239).
link(n4, n5, 14, 457).
link(n5, n4, 14, 457).
link(n4, n15, 23.0, 40).
link(n15, n4, 23.0, 40).
link(n6, n8, 2, 491).
link(n8, n6, 2, 491).
link(n8, n15, 14.0, 319).
link(n15, n8, 14.0, 319).
link(n14, n14, 0.0, inf).
link(n7, n15, 16.0, 75).
link(n15, n7, 16.0, 75).
link(n8, n10, 9, 63).
link(n10, n8, 9, 63).
link(n3, n9, 14.0, 256).
link(n9, n3, 14.0, 256).
link(n4, n9, 14.0, 411).
link(n9, n4, 14.0, 411).
link(n0, n5, 5, 137).
link(n5, n0, 5, 137).
link(n2, n13, 18.0, 377).
link(n13, n2, 18.0, 377).
link(n2, n3, 21.0, 191).
link(n3, n2, 21.0, 191).
link(n0, n1, 19, 231).
link(n1, n0, 19, 231).
link(n1, n2, 22.0, 205).
link(n2, n1, 22.0, 205).
link(n6, n9, 12, 430).
link(n9, n6, 12, 430).
link(n5, n6, 9, 411).
link(n6, n5, 9, 411).
link(n7, n8, 13, 441).
link(n8, n7, 13, 441).
link(n4, n4, 0.0, inf).
link(n3, n12, 17.0, 463).
link(n12, n3, 17.0, 463).
link(n0, n12, 12.0, 493).
link(n12, n0, 12.0, 493).
link(n7, n7, 0.0, inf).
link(n0, n7, 9, 474).
link(n7, n0, 9, 474).
link(n7, n12, 14.0, 26).
link(n12, n7, 14.0, 26).
link(n3, n8, 9.0, 241).
link(n8, n3, 9.0, 241).
link(n11, n14, 16.0, 96).
link(n14, n11, 16.0, 96).
link(n2, n9, 14.0, 296).
link(n9, n2, 14.0, 296).
link(n0, n6, 17, 310).
link(n6, n0, 17, 310).
link(n7, n11, 16.0, 112).
link(n11, n7, 16.0, 112).
link(n2, n12, 17.0, 108).
link(n12, n2, 17.0, 108).
link(n8, n14, 6.0, 213).
link(n14, n8, 6.0, 213).
link(n0, n14, 15.0, 467).
link(n14, n0, 15.0, 467).
link(n8, n9, 5, 355).
link(n9, n8, 5, 355).
link(n8, n12, 8, 487).
link(n12, n8, 8, 487).
link(n10, n12, 10.0, 261).
link(n12, n10, 10.0, 261).
link(n9, n13, 13.0, 356).
link(n13, n9, 13.0, 356).
link(n4, n11, 16.0, 64).
link(n11, n4, 16.0, 64).
link(n12, n12, 0.0, inf).
link(n4, n12, 17.0, 427).
link(n12, n4, 17.0, 427).
link(n2, n14, 20.0, 200).
link(n14, n2, 20.0, 200).
link(n0, n8, 13, 439).
link(n8, n0, 13, 439).
link(n9, n15, 14, 400).
link(n15, n9, 14, 400).
link(n13, n14, 10.0, 496).
link(n14, n13, 10.0, 496).
link(n1, n13, 17.0, 105).
link(n13, n1, 17.0, 105).
link(n12, n15, 18, 48).
link(n15, n12, 18, 48).
link(n9, n10, 7.0, 94).
link(n10, n9, 7.0, 94).
link(n4, n7, 8, 133).
link(n7, n4, 8, 133).
link(n1, n1, 0.0, inf).
link(n10, n15, 12.0, 41).
link(n15, n10, 12.0, 41).
link(n4, n14, 12, 99).
link(n14, n4, 12, 99).
link(n4, n8, 9, 225).
link(n8, n4, 9, 225).
link(n5, n7, 8, 109).
link(n7, n5, 8, 109).
link(n0, n10, 8, 457).
link(n10, n0, 8, 457).
link(n3, n11, 18.0, 291).
link(n11, n3, 18.0, 291).
link(n6, n7, 4, 21).
link(n7, n6, 4, 21).
link(n5, n12, 7, 493).
link(n12, n5, 7, 493).
link(n1, n12, 5, 189).
link(n12, n1, 5, 189).
link(n4, n13, 16, 386).
link(n13, n4, 16, 386).
link(n2, n2, 0.0, inf).
link(n6, n13, 6, 221).
link(n13, n6, 6, 221).
link(n5, n5, 0.0, inf).
link(n5, n10, 3, 242).
link(n10, n5, 3, 242).
link(n6, n11, 12.0, 476).
link(n11, n6, 12.0, 476).
link(n8, n8, 0.0, inf).
link(n3, n10, 18.0, 361).
link(n10, n3, 18.0, 361).
link(n9, n9, 0.0, inf).
link(n10, n11, 14, 483).
link(n11, n10, 14, 483).
link(n7, n14, 8.0, 432).
link(n14, n7, 8.0, 432).
link(n3, n7, 11.0, 394).
link(n7, n3, 11.0, 394).
link(n10, n10, 0.0, inf).
link(n3, n14, 11.0, 495).
link(n14, n3, 11.0, 495).
link(n6, n14, 4, 186).
link(n14, n6, 4, 186).
link(n1, n4, 20.0, 70).
link(n4, n1, 20.0, 70).
link(n5, n11, 9.0, 237).
link(n11, n5, 9.0, 237).
link(n1, n7, 15.0, 261).
link(n7, n1, 15.0, 261).
link(n1, n10, 15.0, 156).
link(n10, n1, 15.0, 156).
link(n12, n14, 13.0, 226).
link(n14, n12, 13.0, 226).
link(n1, n9, 16.0, 413).
link(n9, n1, 16.0, 413).
link(n14, n15, 16.0, 20).
link(n15, n14, 16.0, 20).
link(n5, n8, 9.0, 22).
link(n8, n5, 9.0, 22).
link(n13, n13, 0.0, inf).
link(n8, n13, 8.0, 489).
link(n13, n8, 8.0, 489).
link(n5, n14, 10, 491).
link(n14, n5, 10, 491).
link(n0, n3, 11, 318).
link(n3, n0, 11, 318).
link(n1, n5, 16, 435).
link(n5, n1, 16, 435).
link(n11, n13, 15.0, 412).
link(n13, n11, 15.0, 412).
link(n0, n11, 7, 451).
link(n11, n0, 7, 451).
link(n0, n2, 10, 130).
link(n2, n0, 10, 130).
link(n2, n6, 19.0, 496).
link(n6, n2, 19.0, 496).
link(n11, n12, 16.0, 227).
link(n12, n11, 16.0, 227).
link(n2, n8, 19.0, 44).
link(n8, n2, 19.0, 44).
link(n7, n13, 12, 184).
link(n13, n7, 12, 184).
link(n6, n10, 11.0, 219).
link(n10, n6, 11.0, 219).
link(n5, n15, 9, 340).
link(n15, n5, 9, 340).
link(n10, n14, 13.0, 150).
link(n14, n10, 13.0, 150).
link(n7, n10, 11.0, 99).
link(n10, n7, 11.0, 99).
link(n6, n6, 0.0, inf).
link(n9, n14, 11.0, 143).
link(n14, n9, 11.0, 143).
link(n6, n12, 10, 452).
link(n12, n6, 10, 452).
link(n0, n9, 18, 115).
link(n9, n0, 18, 115).
link(n13, n15, 18.0, 198).
link(n15, n13, 18.0, 198).
link(n3, n3, 0.0, inf).
link(n1, n3, 18.0, 222).
link(n3, n1, 18.0, 222).
link(n3, n15, 19.0, 72).
link(n15, n3, 19.0, 72).
link(n4, n10, 17.0, 473).
link(n10, n4, 17.0, 473).
link(n3, n13, 13.0, 144).
link(n13, n3, 13.0, 144).
link(n2, n4, 19.0, 168).
link(n4, n2, 19.0, 168).
link(n1, n8, 13.0, 345).
link(n8, n1, 13.0, 345).
link(n2, n11, 17.0, 136).
link(n11, n2, 17.0, 136).
link(n11, n11, 0.0, inf).
link(n0, n15, 14.0, 281).
link(n15, n0, 14.0, 281).
link(n1, n15, 21.0, 274).
link(n15, n1, 21.0, 274).
link(n0, n4, 9, 121).
link(n4, n0, 9, 121).
link(n2, n7, 18.0, 309).
link(n7, n2, 18.0, 309).

nodeType(n0, edge).
nodeType(n1, thing).
nodeType(n2, thing).
nodeType(n3, thing).
nodeType(n4, edge).
nodeType(n5, thing).
nodeType(n6, thing).
nodeType(n7, thing).
nodeType(n8, edge).
nodeType(n9, thing).
nodeType(n10, edge).
nodeType(n11, edge).
nodeType(n12, cloud).
nodeType(n13, cloud).
nodeType(n14, edge).
nodeType(n15, thing).

location(n0, de).
location(n1, de).
location(n2, it).
location(n3, de).
location(n4, it).
location(n5, de).
location(n6, de).
location(n7, es).
location(n8, it).
location(n9, it).
location(n10, de).
location(n11, es).
location(n12, it).
location(n13, es).
location(n14, it).
location(n15, es).

provider(n0, ibm).
provider(n1, ibm).
provider(n2, ibm).
provider(n3, azure).
provider(n4, azure).
provider(n5, aws).
provider(n6, ibm).
provider(n7, azure).
provider(n8, azure).
provider(n9, ibm).
provider(n10, ibm).
provider(n11, azure).
provider(n12, azure).
provider(n13, azure).
provider(n14, aws).
provider(n15, azure).
