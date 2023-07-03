!%      (MWD) Module Wrapped and Differentiated
!%
!%      Subroutine
!%      ----------
!%
!%      - binary_search
!%      - compute_rowcol_to_ind_sparse
!%      - get_matrix_nnz
!%      - coo_fill_sparse_matrix
!%      - ac_fill_sparse_matrix
!%      - fill_sparse_matrix
!%      - matrix_to_sparse_matrix
!%      - coo_sparse_matrix_to_matrix
!%      - ac_sparse_matrix_to_matrix
!%      - sparse_matrix_to_matrix
!%      - coo_get_sparse_matrix_dat
!%      - ac_get_sparse_matrix_dat
!%      - get_sparse_matrix_dat

module mwd_sparse_matrix_manipulation

    use md_constant, only: sp
    use mwd_mesh, only: MeshDT
    use mwd_sparse_matrix, only: Sparse_MatrixDT, Sparse_MatrixDT_initialise

    implicit none

    public :: compute_rowcol_to_ind_sparse, matrix_to_sparse_matrix, &
    & sparse_matrix_to_matrix, get_sparse_matrix_dat

contains

    subroutine binary_search(n, vector, vle, ind)

        implicit none

        integer, intent(in) :: n
        integer, dimension(n), intent(in) :: vector
        integer, intent(in) :: vle
        integer, intent(inout) :: ind

        integer :: l, u, m

        ind = -1
        l = 1
        u = n

        do while (l .le. u)

            m = (u + l)/2

            if (vector(m) .lt. vle) then
                l = m + 1

            else if (vector(m) .gt. vle) then
                u = m - 1

            else

                ind = m
                exit

            end if

        end do

    end subroutine binary_search

    subroutine compute_rowcol_to_ind_sparse(mesh)

        !% Notes
        !% -----

        implicit none

        type(MeshDT), intent(inout) :: mesh

        integer :: i, row, col

        i = 0

        do col = 1, mesh%ncol

            do row = 1, mesh%nrow

                if (mesh%active_cell(row, col) .eq. 0) cycle

                i = i + 1
                mesh%rowcol_to_ind_sparse(row, col) = i

            end do

        end do

    end subroutine compute_rowcol_to_ind_sparse

    subroutine get_matrix_nnz(mesh, matrix, zvle, nnz)

        implicit none

        type(MeshDT), intent(in) :: mesh
        real(sp), dimension(mesh%nrow, mesh%ncol), intent(in) :: matrix
        real(sp), intent(in) :: zvle
        integer, intent(inout) :: nnz

        integer :: row, col

        nnz = 0

        do col = 1, mesh%ncol

            do row = 1, mesh%nrow

                if (mesh%active_cell(row, col) .eq. 0 .or. abs(matrix(row, col) - zvle) .le. 0._sp) cycle

                nnz = nnz + 1

            end do

        end do

    end subroutine get_matrix_nnz

    subroutine coo_fill_sparse_matrix(mesh, matrix, sparse_matrix)

        type(MeshDT), intent(in) :: mesh
        real(sp), dimension(mesh%nrow, mesh%ncol), intent(in) :: matrix
        type(Sparse_MatrixDT), intent(inout) :: sparse_matrix

        integer :: row, col, i

        i = 0

        do col = 1, mesh%ncol

            do row = 1, mesh%nrow

                if (mesh%active_cell(row, col) .eq. 0 .or. &
                & abs(matrix(row, col) - sparse_matrix%zvle) .le. 0._sp) cycle

                i = i + 1

                sparse_matrix%ind(i) = mesh%rowcol_to_ind_sparse(row, col)
                sparse_matrix%dat(i) = matrix(row, col)

            end do

        end do

    end subroutine coo_fill_sparse_matrix

    subroutine ac_fill_sparse_matrix(mesh, matrix, sparse_matrix)

        type(MeshDT), intent(in) :: mesh
        real(sp), dimension(mesh%nrow, mesh%ncol), intent(in) :: matrix
        type(Sparse_MatrixDT), intent(inout) :: sparse_matrix

        integer :: row, col, i

        i = 0

        do col = 1, mesh%ncol

            do row = 1, mesh%nrow

                if (mesh%active_cell(row, col) .eq. 0) cycle

                i = i + 1
                sparse_matrix%dat(i) = matrix(row, col)

            end do

        end do

    end subroutine ac_fill_sparse_matrix

    subroutine fill_sparse_matrix(mesh, matrix, sparse_matrix)

        type(MeshDT), intent(in) :: mesh
        real(sp), dimension(mesh%nrow, mesh%ncol), intent(in) :: matrix
        type(Sparse_MatrixDT), intent(inout) :: sparse_matrix

        if (sparse_matrix%coo_fmt) then

            call coo_fill_sparse_matrix(mesh, matrix, sparse_matrix)

        else

            call ac_fill_sparse_matrix(mesh, matrix, sparse_matrix)

        end if

    end subroutine fill_sparse_matrix

    subroutine matrix_to_sparse_matrix(mesh, matrix, zvle, sparse_matrix)

        implicit none

        type(MeshDT), intent(in) :: mesh
        real(sp), dimension(mesh%nrow, mesh%ncol), intent(in) :: matrix
        real(sp), intent(in) :: zvle
        type(Sparse_MatrixDT), intent(inout) :: sparse_matrix

        integer :: nnz, n
        logical :: coo_fmt

        call get_matrix_nnz(mesh, matrix, zvle, nnz)

        !% Do not need to cast to real
        if (nnz .le. mesh%nac/2) then

            n = nnz
            coo_fmt = .true.

        else

            n = mesh%nac
            coo_fmt = .false.

        end if

        call Sparse_MatrixDT_initialise(sparse_matrix, n, coo_fmt, zvle)

        call fill_sparse_matrix(mesh, matrix, sparse_matrix)

    end subroutine matrix_to_sparse_matrix

    subroutine coo_sparse_matrix_to_matrix(mesh, sparse_matrix, matrix)

        implicit none

        type(MeshDT), intent(in) :: mesh
        type(Sparse_MatrixDT), intent(in) :: sparse_matrix
        real(sp), dimension(mesh%nrow, mesh%ncol), intent(inout) :: matrix

        integer :: row, col, i, next_ind

        i = 0
        next_ind = 1

        do col = 1, mesh%ncol

            do row = 1, mesh%nrow

                if (mesh%active_cell(row, col) .eq. 0) cycle

                i = i + 1

                if (i .ne. sparse_matrix%ind(next_ind)) cycle

                matrix(row, col) = sparse_matrix%dat(next_ind)
                next_ind = next_ind + 1

                if (next_ind .gt. sparse_matrix%n) return

            end do

        end do

    end subroutine coo_sparse_matrix_to_matrix

    subroutine ac_sparse_matrix_to_matrix(mesh, sparse_matrix, matrix)

        implicit none

        type(MeshDT), intent(in) :: mesh
        type(Sparse_MatrixDT), intent(in) :: sparse_matrix
        real(sp), dimension(mesh%nrow, mesh%ncol), intent(inout) :: matrix

        integer :: row, col, i

        i = 0

        do col = 1, mesh%ncol

            do row = 1, mesh%nrow

                if (mesh%active_cell(row, col) .eq. 0) cycle

                i = i + 1
                matrix(row, col) = sparse_matrix%dat(i)

            end do

        end do

    end subroutine ac_sparse_matrix_to_matrix

    subroutine sparse_matrix_to_matrix(mesh, sparse_matrix, matrix)

        implicit none

        type(MeshDT), intent(in) :: mesh
        type(Sparse_MatrixDT), intent(in) :: sparse_matrix
        real(sp), dimension(mesh%nrow, mesh%ncol), intent(inout) :: matrix

        matrix = sparse_matrix%zvle

        if (sparse_matrix%n .eq. 0) return

        if (sparse_matrix%coo_fmt) then

            call coo_sparse_matrix_to_matrix(mesh, sparse_matrix, matrix)

        else

            call ac_sparse_matrix_to_matrix(mesh, sparse_matrix, matrix)

        end if

    end subroutine sparse_matrix_to_matrix

    subroutine coo_get_sparse_matrix_dat(mesh, row, col, sparse_matrix, res)

        implicit none

        type(MeshDT), intent(in) :: mesh
        integer, intent(in) :: row, col
        type(Sparse_MatrixDT), intent(in) :: sparse_matrix
        real(sp), intent(inout) :: res

        integer :: k, ind

        k = mesh%rowcol_to_ind_sparse(row, col)

        call binary_search(sparse_matrix%n, sparse_matrix%ind, k, ind)

        if (ind .ne. -1) res = sparse_matrix%dat(ind)

    end subroutine coo_get_sparse_matrix_dat

    subroutine ac_get_sparse_matrix_dat(mesh, row, col, sparse_matrix, res)

        implicit none

        type(MeshDT), intent(in) :: mesh
        integer, intent(in) :: row, col
        type(Sparse_MatrixDT), intent(in) :: sparse_matrix
        real(sp), intent(inout) :: res

        integer :: k

        k = mesh%rowcol_to_ind_sparse(row, col)

        res = sparse_matrix%dat(k)

    end subroutine ac_get_sparse_matrix_dat

    subroutine get_sparse_matrix_dat(mesh, row, col, sparse_matrix, res)

        implicit none

        type(MeshDT), intent(in) :: mesh
        integer, intent(in) :: row, col
        type(Sparse_MatrixDT), intent(in) :: sparse_matrix
        real(sp), intent(inout) :: res

        res = sparse_matrix%zvle

        if (sparse_matrix%n .eq. 0) return

        if (sparse_matrix%coo_fmt) then

            call coo_get_sparse_matrix_dat(mesh, row, col, sparse_matrix, res)

        else

            call ac_get_sparse_matrix_dat(mesh, row, col, sparse_matrix, res)

        end if

    end subroutine get_sparse_matrix_dat

end module mwd_sparse_matrix_manipulation