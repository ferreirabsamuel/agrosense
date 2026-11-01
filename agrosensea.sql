
create or replace view umidade_perfil_hora as
select s.id_estacao,
       l.horario_utc,
       avg(l.umidade_solo) as umidade_perfil,
       count(*) as sensores
from leitura_solo l
join sensor s on s.id_sensor = l.id_sensor
where l.umidade_solo is not null
group by s.id_estacao, l.horario_utc
having count(*) = (
    select count(*) from sensor s2
    where s2.id_estacao = s.id_estacao
);

create view umidade_atual as
select u.*
from umidade_perfil_hora u
where u.horario_utc = (
    select max(u2.horario_utc)
    from umidade_perfil_hora u2
    where u2.id_estacao = u.id_estacao
);

create table clima_diario (
    id_clima_diario int not null auto_increment,
    id_estacao int not null,
    data date not null comment 'dia local da estacao (mst, utc-7)',
    temp_media_c decimal(5,2) null comment 'temperatura media do ar, em graus celsius',
    temp_max_c decimal(5,2) null comment 'temperatura maxima do ar, em graus celsius',
    temp_min_c decimal(5,2) null comment 'temperatura minima do ar, em graus celsius',
    umid_max_pct decimal(5,2) null comment 'umidade relativa maxima do dia, de 0 a 100',
    umid_min_pct decimal(5,2) null comment 'umidade relativa minima do dia, de 0 a 100',
    chuva_mm decimal(6,2) null comment 'chuva do dia, em milimetros',
    eto_mm decimal(5,2) null comment 'evapotranspiracao de referencia do dia, em milimetros',
    primary key (id_clima_diario),
    unique key uk_clima_diario_estacao_data (id_estacao, data),
    constraint fk_clima_diario_estacao foreign key (id_estacao) references estacao (id_estacao),
    constraint ck_clima_diario_umidade check (umid_max_pct between 0 and 100 and umid_min_pct between 0 and 100),
    constraint ck_clima_diario_chuva check (chuva_mm >= 0)
);

insert into clima_diario (id_estacao, data, temp_media_c, temp_max_c, temp_min_c, umid_max_pct, umid_min_pct, chuva_mm, eto_mm)
select id_estacao, '1900-01-01', 9.25, 16.98, -2.60, 95.0, 23.2, 0.25, 2.84
from estacao
where codigo = 'HYD01';

delete from clima_diario
where id_clima_diario > 0
  and data = '1900-01-01';

insert into clima_diario (id_estacao, data, umid_max_pct)
select id_estacao, '1900-01-02', 150
from estacao
where codigo = 'HYD01';

select count(*) from clima_diario;

create table praga (
    id_praga int not null auto_increment,
    nome_comum varchar(80) not null comment 'nome popular da praga, em portugues',
    nome_cientifico varchar(120) not null comment 'nome cientifico, que identifica a praga sem ambiguidade',
    tipo varchar(10) not null default 'inseto' comment 'inseto, fungo ou outro',
    primary key (id_praga),
    unique key uk_praga_nome_cientifico (nome_cientifico),
    constraint ck_praga_tipo check (tipo in ('inseto', 'fungo', 'outro'))
);

insert into praga (nome_comum, nome_cientifico, tipo) values
    ('gorgulho-da-alfafa', 'Hypera postica', 'inseto');
    
select * from praga;

create table observacao_praga (
    id_observacao int not null auto_increment,
    id_estacao int not null,
    id_praga int not null,
    observado_em date not null comment 'dia da visita ao campo',
    estagio varchar(20) not null default 'nao se aplica' comment 'fase de vida contada: ovo, larva, pupa ou adulto',
    quantidade int not null comment 'contagem por amostra padrao do campo; 0 quando a visita nao encontrou a praga',
    origem varchar(10) not null default 'campo' comment 'campo para registro real, simulado para dado de teste',
    nota varchar(200) null comment 'observacao livre do campo',
    registrado_em datetime not null default current_timestamp comment 'quando o registro foi gravado no sistema',
    primary key (id_observacao),
    unique key uk_observacao_praga_visita (id_estacao, id_praga, observado_em, estagio, origem),
    constraint fk_observacao_praga_estacao foreign key (id_estacao) references estacao (id_estacao),
    constraint fk_observacao_praga_praga foreign key (id_praga) references praga (id_praga),
    constraint ck_observacao_praga_quantidade check (quantidade >= 0),
    constraint ck_observacao_praga_estagio check (estagio in ('ovo', 'larva', 'pupa', 'adulto', 'nao se aplica')),
    constraint ck_observacao_praga_origem check (origem in ('campo', 'simulado'))
);

insert into observacao_praga (id_estacao, id_praga, observado_em, estagio, quantidade, origem)
select e.id_estacao, p.id_praga, '1900-01-01', 'larva', 0, 'simulado'
from estacao e, praga p
where e.codigo = 'HYD01' and p.nome_cientifico = 'Hypera postica';

delete from observacao_praga
where id_observacao > 0
  and observado_em = '1900-01-01';
  
  select count(*), min(data), max(data) from clima_diario;
select * from clima_diario where data = '2026-10-23';