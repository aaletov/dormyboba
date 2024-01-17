INSERT INTO public.dormyboba_role (role_name) VALUES
    ('student'),
    ('council_member'),
    ('admin');

INSERT INTO public.academic_type (type_id, type_name) VALUES
    (3, 'Бакалавриат'),
    (4, 'Магистратура'),
    (5, 'Специалитет'),
    (6, 'Аспирантура');

INSERT INTO public.institute (institute_id, institute_name) VALUES
    (31, 'ИСИ'),
    (32, 'ИЭ'),
    (33, 'ИММиТ'),
    (37, 'ИПМЭиТ'),
    (38, 'ГИ'),
    (47, 'ИБСиБ'),
    (49, 'ИЭиТ'),
    (50, 'Физмех'),
    (51, 'ИКНК');

INSERT INTO public.dormyboba_user (user_id, role_id) SELECT 608713, role_id
    FROM public.dormyboba_role WHERE role_name = 'admin';

